from asyncio import Lock
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from hashlib import sha256
from inspect import isawaitable
from math import ceil
from typing import TypeAlias, TypeVar

from fastapi import Request, Response
from fastapi_pagination.utils import is_async_callable
from pyrate_limiter import AbstractBucket, BucketFactory, Limiter, Rate, RateItem
from pyrate_limiter.buckets import RedisBucket
from redis.asyncio import Redis
from starlette.concurrency import run_in_threadpool

from backend.common.exception import errors
from backend.common.response.response_code import StandardResponseCode
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.request_parse import get_request_ip

IdentifierCallable: TypeAlias = Callable[[Request], str] | Callable[[Request], Awaitable[str]]
CallbackCallable: TypeAlias = (
    Callable[[Request, Response, int], None] | Callable[[Request, Response, int], Awaitable[None]]
)
T = TypeVar('T')

REQUEST_LIMITER_BUCKET_CACHE_MAX_SIZE = 4096
REQUEST_LIMITER_BUCKET_CACHE_BUFFER_MS = 10_000


@dataclass(slots=True)
class RedisBucketState:
    """Cached Redis bucket state."""

    bucket: RedisBucket
    last_seen: int


async def _maybe_await(value: T | Awaitable[T]) -> T:
    """
    Support synchronous and asynchronous values

    :param value: Synchronous value or Awaitable object
    :return:
    """
    if isawaitable(value):
        return await value
    return value


async def _redis_time_ms(redis: Redis) -> int:
    """
    Get the Redis server's current time

    :return:
    """
    seconds, microseconds = await redis.time()
    return seconds * 1000 + microseconds // 1000


class RedisTimeBucket(RedisBucket):
    """Redis bucket that uses the Redis server clock."""

    async def now(self) -> int:
        """Get the current time from the Redis server."""
        return await _redis_time_ms(self.redis)


class RedisBucketFactory(BucketFactory):
    """Route request identifiers to independent Redis buckets."""

    def __init__(
        self,
        rates: list[Rate],
        bucket_key: str,
        max_cache_size: int = REQUEST_LIMITER_BUCKET_CACHE_MAX_SIZE,
    ) -> None:
        """
        Initialize the Redis bucket factory

        :param rates: pyrate_limiter Rate object list
        :param bucket_key: Redis key prefix
        :param max_cache_size: Maximum number of locally cached buckets
        :return:
        """
        self.rates = rates
        self.bucket_key = f'{bucket_key}:{self._rate_key(rates)}'
        self.max_cache_size = max(1, max_cache_size)
        self.cache_ttl = max(rate.interval for rate in rates) + REQUEST_LIMITER_BUCKET_CACHE_BUFFER_MS
        self.lock = Lock()
        self.buckets: OrderedDict[str, RedisBucketState] = OrderedDict()

    async def wrap_item(self, name: str, weight: int = 1) -> RateItem:
        """
        Wrap a rate-limit item

        :param name: Rate-limit identifier
        :param weight: Request weight
        :return:
        """
        return RateItem(name, await _redis_time_ms(redis_client), weight=weight)

    async def get(self, item: RateItem) -> RedisBucket:
        """
        Get the Redis bucket for the identifier

        :param item: rate-limit item
        :return:
        """
        bucket_key = self._bucket_key(item.name)
        now = await _redis_time_ms(redis_client)

        async with self.lock:
            state = self.buckets.get(bucket_key)
            if state is not None:
                state.last_seen = now
                self.buckets.move_to_end(bucket_key)
                return state.bucket

            bucket_result = RedisTimeBucket.init(
                rates=self.rates,
                redis=redis_client,
                bucket_key=bucket_key,
            )
            bucket = await _maybe_await(bucket_result)
            self.buckets[bucket_key] = RedisBucketState(bucket=bucket, last_seen=now)
            self.schedule_leak(bucket)
            await self._evict(now)
            return bucket

    async def get_bucket(self, name: str) -> RedisBucket:
        """
        Get the Redis bucket for the identifier

        :param name: Rate-limit identifier
        :return:
        """
        return await self.get(await self.wrap_item(name))

    async def _evict(self, now: int) -> None:
        """
        Evict the local bucket cache

        :param now: Current timestamp in milliseconds
        :return:
        """
        for bucket_key, state in list(self.buckets.items()):
            if now - state.last_seen <= self.cache_ttl:
                continue
            await self._dispose(bucket_key, state, now, cleanup=True)

        while len(self.buckets) > self.max_cache_size:
            bucket_key, state = next(iter(self.buckets.items()))
            await self._dispose(bucket_key, state, now, cleanup=False)

    async def _dispose(self, bucket_key: str, state: RedisBucketState, now: int, *, cleanup: bool) -> None:
        """
        Remove the local bucket and optionally clean expired Redis data

        :param bucket_key: Redis bucket key
        :param state: Cached Redis bucket state
        :param now: Current timestamp in milliseconds
        :param cleanup: Whether to clean expired Redis data
        :return:
        """
        self.buckets.pop(bucket_key, None)
        self.dispose(state.bucket)
        if cleanup:
            await _maybe_await(state.bucket.leak(now))
            if await _maybe_await(state.bucket.count()) == 0:
                await _maybe_await(state.bucket.flush())

    def _bucket_key(self, name: str) -> str:
        """
        Generate the Redis bucket key for an identifier

        :param name: Rate-limit identifier
        :return:
        """
        digest = sha256(name.encode()).hexdigest()
        return f'{self.bucket_key}:{digest}'

    @staticmethod
    def _rate_key(rates: list[Rate]) -> str:
        """
        Generate the Redis key fragment for a rate-limit policy

        :param rates: pyrate_limiter Rate object list
        :return:
        """
        value = ':'.join(f'{rate.limit}:{rate.interval}' for rate in sorted(rates, key=lambda rate: rate.interval))
        return sha256(value.encode()).hexdigest()


def default_identifier(request: Request) -> str:
    """
    default identifier

     :param request: FastAPI request object
     :return:
    """
    ip = get_request_ip(request)
    return f'{ip}:{request.scope["path"]}'


def default_callback(request: Request, response: Response, retry_after: int) -> None:
    """
    Default callback

    :param request: FastAPI request object
    :param response: FastAPI response object
    :param retry_after: Number of seconds to retry next time
    :return:
    """
    raise errors.HTTPError(
        code=StandardResponseCode.HTTP_429,
        msg='The request is too frequent, please try again later.',
        headers={'Retry-After': str(retry_after)},
    )


class RateLimiter:
    """rateLimiter"""

    def __init__(
        self,
        *rates: Rate,
        identifier: IdentifierCallable = default_identifier,
        bucket: AbstractBucket | None = None,
        limiter: Limiter | None = None,
        callback: CallbackCallable = default_callback,
    ) -> None:
        """
        Initialize rate limiter

        :param rates: pyrate_limiter Rate object, supports passing in single or multiple
        :param identifier: custom identifier function
        :param bucket: pyrate_limiter AbstractBucket instance
        :param limiter: pyrate_limiter Limiter instance
        :param callback: Custom current limiting callback function
        :return:
        """
        if limiter is None and not rates and bucket is None:
            raise errors.ServerError(msg='At least one Rate, bucket or limiter instance needs to be passed in')
        self.rates = list(rates)
        self.identifier = identifier
        self.bucket = bucket
        self.limiter = limiter
        self.callback = callback
        self.bucket_factory: RedisBucketFactory | None = None

    async def __call__(self, request: Request, response: Response) -> None:
        """
        Perform request current limit check

        :param request: FastAPI request object
        :param response: FastAPI response object
        :return:
        """
        if self.limiter is None:
            if self.bucket is None:
                self.bucket_factory = RedisBucketFactory(
                    rates=self.rates,
                    bucket_key=f'{settings.REQUEST_LIMITER_REDIS_PREFIX}',
                )
                self.limiter = Limiter(self.bucket_factory)
            else:
                self.limiter = Limiter(self.bucket)

        if is_async_callable(self.identifier):
            identifier = await self.identifier(request)
        else:
            identifier = await run_in_threadpool(self.identifier, request)

        acquired = await self.limiter.try_acquire_async(identifier, blocking=False)
        if not acquired:
            retry_after = await self._retry_after(identifier)
            if is_async_callable(self.callback):
                await self.callback(request, response, retry_after)
            else:
                await run_in_threadpool(self.callback, request, response, retry_after)

    async def _retry_after(self, identifier: str) -> int:
        """
        Calculate current limit retry waiting time

        :param identifier: current limit identifier
        :return:
        """
        if self.bucket_factory is not None:
            failing_rate = (await self.bucket_factory.get_bucket(identifier)).failing_rate
        elif self.bucket is not None:
            failing_rate = self.bucket.failing_rate
        else:
            failing_rate = None

        if failing_rate is not None:
            return ceil(failing_rate.interval / 1000)

        if self.limiter is not None:
            for bucket in self.limiter.buckets():
                if bucket.failing_rate is not None:
                    return ceil(bucket.failing_rate.interval / 1000)

        if self.rates:
            return ceil(max(rate.interval for rate in self.rates) / 1000)

        return 1
