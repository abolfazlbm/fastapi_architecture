import functools

from collections.abc import Callable, Sequence
from typing import Any, ParamSpec, TypeVar

from msgspec import json

from backend.common.cache.local import local_cache_manager
from backend.common.cache.pubsub import cache_pubsub_manager
from backend.common.context import ctx
from backend.common.exception import errors
from backend.common.log import log
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.serializers import select_columns_serialize, select_list_serialize

P = ParamSpec('P')
T = TypeVar('T')


def _build_cache_key(
    name: str,
    key: str | None,
    key_builder: Callable[..., str] | None,
    *args: Any,
    **kwargs: Any,
) -> str:
    """Build cache Key"""
    if key:
        if '.' in key:
            param, field = key.split('.', 1)
            value = kwargs.get(param)
            if value is None:
                raise errors.ServerError(msg=f'Cache key build failed, parameter "{param}" does not exist or has an empty value')

            if isinstance(value, list):
                raise errors.ServerError(msg='Cache key build failed: Extracting fields from lists is not supported, please use key_builder to handle list parameters')

            if hasattr(value, field):
                value = getattr(value, field)
            elif isinstance(value, dict) and field in value:
                value = value[field]
            else:
                raise errors.ServerError(msg=f'Cache key build failed, field does not exist in object "{field}"')
        else:
            value = kwargs.get(key)
            if value is None:
                raise errors.ServerError(msg=f'Cache key construction failed, parameter "{key}" does not exist or has an empty value')

        return f'{name}:{value}'

    if key_builder:
        return f'{name}:{key_builder(*args, **kwargs)}'

    return name


def _serialize_result(result: Any) -> bytes:
    """
    Serialize cached results

    :param result: the result that needs to be serialized
    :return:
    """
    # SQLAlchemy query table
    if hasattr(result, '__table__'):
        return json.encode(select_columns_serialize(result))

    # SQLAlchemy query list
    if (
        isinstance(result, Sequence)
        and not isinstance(result, (str, bytes))
        and len(result) > 0
        and hasattr(result[0], '__table__')
    ):
        return json.encode(select_list_serialize(result))

    # Basic Type
    return json.encode(result)


def _deserialize_result(value: bytes) -> Any:
    """
    Deserialize cached results

    :param value: cache results
    :return:
    """
    try:
        return json.decode(value)
    except Exception:
        return value


def user_key_builder() -> str:
    """Generate cache Key based on current user ID"""
    user_id = ctx.user_id
    if user_id is None:
        raise errors.ServerError(msg='User cache key construction failed')
    return str(user_id)


def cached(  # noqa: C901
    name: str,
    *,
    key: str | None = None,
    key_builder: Callable[..., str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    cache decorator

    :param name: cache name (usually cache Key prefix)
    :param key: Get the value of the specified parameter name from the method parameter as the cache Key, mutually exclusive with key_builder
    :param key_builder: Custom Key generation function, mutually exclusive with key
    :return:
    """
    if key is not None and key_builder is not None:
        raise errors.ServerError(msg='Cache key and key_builder cannot be used at the same time')

    def decorator(func: Callable[P, T]) -> Callable[P, T]:  # noqa: C901
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            cache_key = _build_cache_key(name, key, key_builder, *args, **kwargs)

            # L1: local cache
            if settings.CACHE_LOCAL_ENABLED:
                local_value = local_cache_manager.get(cache_key)
                if local_value is not None:
                    return local_value

            # L2: Redis cache
            try:
                redis_value = await redis_client.get(cache_key)
                if redis_value is not None:
                    result = _deserialize_result(redis_value)
                    # Backfill L1
                    if settings.CACHE_LOCAL_ENABLED:
                        local_cache_manager.set(cache_key, result)
                    return result
            except Exception as e:
                log.warning(f'[Cache] GET error: {e}')

            # cache miss
            result = await func(*args, **kwargs)

            if result is not None:
                try:
                    serialized_result = _serialize_result(result)
                    deserialized_result = _deserialize_result(serialized_result)

                    # Backfill L1
                    if settings.CACHE_LOCAL_ENABLED:
                        local_cache_manager.set(cache_key, deserialized_result)

                    # Backfill L2
                    if settings.CACHE_REDIS_TTL:
                        await redis_client.set(cache_key, serialized_result, ex=settings.CACHE_REDIS_TTL)
                    else:
                        await redis_client.set(cache_key, serialized_result)
                except Exception as e:
                    log.warning(f'[Cache] SET error: {e}')

            return result

        return wrapper

    return decorator


def cache_invalidate(  # noqa: C901
    name: str,
    *,
    key: str | None = None,
    key_builder: Callable[..., str] | None = None,
    atomic: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Cache invalidation decorator

    :param name: cache name (usually cache Key prefix)
    :param key: Get the value of the specified parameter name from the method parameter as the cache Key, mutually exclusive with key_builder
    :param key_builder: Custom Key generation function, mutually exclusive with key
    :param atomic: Whether to ensure cache atomicity
    :return:
    """
    if key is not None and key_builder is not None:
        raise errors.ServerError(msg='Cache key and key_builder cannot be used at the same time')

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result = await func(*args, **kwargs)

            # Try invalidating cache
            invalidate_success = False
            invalidate_error = None

            try:
                invalidate_key = _build_cache_key(name, key, key_builder, *args, **kwargs)

                # L1 cache invalidation
                if settings.CACHE_LOCAL_ENABLED:
                    if invalidate_key == name:
                        local_cache_manager.delete_prefix(invalidate_key)
                    else:
                        local_cache_manager.delete(invalidate_key)

                # Broadcast invalidation message (notify other nodes to clear local cache)
                if settings.CACHE_LOCAL_ENABLED:
                    if invalidate_key == name:
                        await cache_pubsub_manager.publish_invalidation(invalidate_key, is_delete_prefix=True)
                    else:
                        await cache_pubsub_manager.publish_invalidation(invalidate_key, is_delete_prefix=False)

                # L2 cache invalidation
                if invalidate_key == name:
                    await redis_client.delete_prefix(invalidate_key)
                else:
                    await redis_client.delete(invalidate_key)

            except Exception as e:
                log.error(f'[Cache] INVALIDATE error: {e}')
                invalidate_error = e
            else:
                invalidate_success = True

            # atomicity check
            if atomic and not invalidate_success:
                raise errors.ServerError(msg='Cache invalidation failed, data may be inconsistent', data=invalidate_error)

            return result

        return wrapper

    return decorator
