import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from backend.common.log import log
from backend.core.conf import settings


class RedisCli(Redis):
    """Redis Client"""

    def __init__(self) -> None:
        """Initialize Redis Client"""
        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            socket_keepalive=True, # Stay connected
            health_check_interval=30, # Health check interval
            decode_responses=True, # Transcoding utf-8
        )

    async def open(self) -> None:
        """Trigger initialization connection"""
        try:
            await self.ping()
        except TimeoutError:
            log.error('❌ Database redis connection timed out')
            sys.exit()
        except AuthenticationError:
            log.error('❌ Database redis connection authentication failed')
            sys.exit()
        except Exception as e:
            log.error('❌ Database redis connection exception {}', e)
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None, batch_size: int = 1000) -> None:
        """
        Delete all keys of the specified prefix

        :param prefix: the key prefix to be deleted
        :param exclude: Key or list of keys to exclude
        :param batch_size: The size of batch deletion to avoid Redis blocking caused by deleting too many keys at one time
        :return:
        """
        exclude_set = set(exclude) if isinstance(exclude, list) else {exclude} if isinstance(exclude, str) else set()
        batch_keys = []

        async for key in self.scan_iter(match=f'{prefix}*'):
            if key not in exclude_set:
                batch_keys.append(key)

                if len(batch_keys) >= batch_size:
                    await self.delete(*batch_keys)
                    batch_keys.clear()

        if batch_keys:
            await self.delete(*batch_keys)

    async def get_prefix(self, prefix: str, count: int = 100) -> list[str]:
        """
        Get all keys with the specified prefix

        :param prefix: key prefix to search for
        :param count: The number of batches scanned each time. The larger the value, the faster the scanning speed, but it will occupy more server resources.
        :return:
        """
        return [key async for key in self.scan_iter(match=f'{prefix}*', count=count)]


# Create a redis client singleton
redis_client: RedisCli = RedisCli()
