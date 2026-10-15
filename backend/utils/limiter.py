from asyncio import Lock
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from hashlib import sha256
from inspect import isawaitable
from math import ceil

from fastapi import Request, Response
from fastapi_pagination.utils import is_async_callable
from pyrate_limiter import BucketFactory, Rate, RateItem
from pyrate_limiter.buckets import RedisBucket
from redis.asyncio import Redis
from starlette.concurrency import run_in_threadpool

from backend.common.exception import errors
from backend.common.response.response_code import StandardResponseCode
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.request_parse import get_request_ip

type IdentifierCallable = Callable[[Request], str | Awaitable[str]]
type CallbackCallable = Callable[[Request, Response, int], Awaitable[None] | None]

_REQUEST_LIMITER_BUCKET_CACHE_MAX_SIZE = 4096
_REQUEST_LIMITER_BUCKET_CACHE_BUFFER_MS = 10_000


@dataclass(slots=True)
class RedisBucketState:
    """Redis bucket cache state"""

    bucket: RedisBucket
    last_seen: int


async def _maybe_await[T](value: T | Awaitable[T]) -> T:
    """
    Support both synchronous and asynchronous values

    :param value: Synchronous value or Awaitable object
    :return:
    """
    if isawaitable(value):
        return await value
    return value


async def _redis_time_ms(redis: Redis) -> int:
    """
    Get the current Redis server time

    :return:
    """
    seconds, microseconds = await redis.time()
    return seconds * 1000 + microseconds // 1000


class RedisTimeBucket(RedisBucket):
    """Redis bucket using Redis server time"""

    async def now(self) -> int:
        """Get the current Redis server time"""
        return await _redis_time_ms(self.redis)


class RedisBucketFactory(BucketFactory):
    """Route each request identifier to a separate Redis bucket"""

    def __init__(
        self,
        rates: list[Rate],
        bucket_key: str,
        max_cache_size: int = _REQUEST_LIMITER_BUCKET_CACHE_MAX_SIZE,
    ) -> None:
        """
        Initialize the Redis bucket factory

        :param rates: List of pyrate_limiter Rate objects
        :param bucket_key: Redis key prefix
        :param max_cache_size: Maximum number of locally cached buckets
        :return:
        """
        self.rates = rates
        self.bucket_key = f'{bucket_key}:{self._rate_key(rates)}'
        self.max_cache_size = max(1, max_cache_size)
        self.cache_ttl = max(rate.interval for rate in rates) + _REQUEST_LIMITER_BUCKET_CACHE_BUFFER_MS
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

        :param item: Rate-limit item
        :return:
        """
        bucket_key = self._bucket_key(item.name)
        # Reuse the Redis time already fetched by wrap_item to save a round trip
        now = item.timestamp

        async with self.lock:
            state = self.buckets.get(bucket_key)
            if state is not None:
                state.last_seen = now
                self.buckets.move_to_end(bucket_key)
                return state.bucket

        # Perform Redis I/O outside the lock so rate-limit requests do not all queue behind script_load
        bucket = await _maybe_await(
            RedisTimeBucket.init(
                rates=self.rates,
                redis=redis_client,
                bucket_key=bucket_key,
            )
        )

        async with self.lock:
            # Use the first entry when the same bucket is initialized concurrently
            state = self.buckets.get(bucket_key)
            if state is not None:
                state.last_seen = now
                self.buckets.move_to_end(bucket_key)
                return state.bucket
            self.buckets[bucket_key] = RedisBucketState(bucket=bucket, last_seen=now)
            self.schedule_leak(bucket)
            disposed = self._evict(now)

        for state in disposed:
            await self._cleanup(state.bucket, now)
        return bucket

    async def get_bucket(self, name: str) -> RedisBucket:
        """
        Get the Redis bucket for the identifier

        :param name: Rate-limit identifier
        :return:
        """
        return await self.get(await self.wrap_item(name))

    def _evict(self, now: int) -> list[RedisBucketState]:
        """
        Evict local bucket cache entries by updating memory only, without Redis I/O

        :param now: Current timestamp in milliseconds
        :return:
        """
        expired: list[RedisBucketState] = []
        for bucket_key, state in list(self.buckets.items()):
            if now - state.last_seen <= self.cache_ttl:
                continue
            self.buckets.pop(bucket_key, None)
            self.dispose(state.bucket)
            expired.append(state)

        while len(self.buckets) > self.max_cache_size:
            _, state = self.buckets.popitem(last=False)
            self.dispose(state.bucket)
        return expired

    @staticmethod
    async def _cleanup(bucket: RedisBucket, now: int) -> None:
        """
        Clean up expired Redis data for evicted buckets

        :param bucket: Redis bucket
        :param now: Current timestamp in milliseconds
        :return:
        """
        await _maybe_await(bucket.leak(now))
        if await _maybe_await(bucket.count()) == 0:
            await _maybe_await(bucket.flush())

    def _bucket_key(self, name: str) -> str:
        """
        Generate the Redis bucket key for the identifier

        :param name: Rate-limit identifier
        :return:
        """
        digest = sha256(name.encode()).hexdigest()
        return f'{self.bucket_key}:{digest}'

    @staticmethod
    def _rate_key(rates: list[Rate]) -> str:
        """
        Generate the Redis key fragment for the rate-limit policies

        :param rates: List of pyrate_limiter Rate objects
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
        callback: CallbackCallable = default_callback,
    ) -> None:
        """
        Initialize rate limiter

        :param rates: One or more rate-limit policies
        :param identifier: Custom identifier function
        :param callback: Custom rate-limit callback function
        :return:
        """
        if not rates:
            raise errors.ServerError(msg='At least one Rate must be provided')
        self.identifier = identifier
        self.callback = callback
        self.bucket_factory = RedisBucketFactory(list(rates), settings.REQUEST_LIMITER_REDIS_PREFIX)

    async def __call__(self, request: Request, response: Response) -> None:
        """
        Perform request current limit check

        :param request: FastAPI request object
        :param response: FastAPI response object
        :return:
        """
        if self.identifier is default_identifier:
            identifier = self.identifier(request)
        elif is_async_callable(self.identifier):
            identifier = await self.identifier(request)
        else:
            identifier = await run_in_threadpool(self.identifier, request)

        item = await self.bucket_factory.wrap_item(identifier)
        bucket = await self.bucket_factory.get(item)
        decision = await bucket.put_decision(item)
        if decision.allowed:
            return

        wait_ms = decision.retry_after_ms
        if wait_ms is None:
            wait_ms = max(rate.interval for rate in self.bucket_factory.rates)
        retry_after = max(1, ceil(wait_ms / 1000))
        if self.callback is default_callback:
            self.callback(request, response, retry_after)
        elif is_async_callable(self.callback):
            await self.callback(request, response, retry_after)
        else:
            await run_in_threadpool(self.callback, request, response, retry_after)
