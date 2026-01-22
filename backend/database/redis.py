import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from backend.common.log import log
from backend.core.conf import settings


class RedisCli(Redis):
    """Redis Client"""

    def __init__(
        self,
        host: str = settings.REDIS_HOST,
        port: int = settings.REDIS_PORT,
        password: str = settings.REDIS_PASSWORD,
        db: int = settings.REDIS_DATABASE,
        socket_timeout: int = settings.REDIS_TIMEOUT,
        socket_connect_timeout: int = settings.REDIS_TIMEOUT,
        *,
        socket_keepalive: bool = True,
        health_check_interval: int = 30,
        decode_responses: bool = True,
    ) -> None:
        """
        Initialize the Redis client

        :param host: host address of the Redis server
        :param port: the port number of the Redis server
        :param password: Redis authentication password
        :param db: Redis logical database index used
        :param socket_timeout: timeout for Socket read and write operations
        :param socket_connect_timeout: timeout when establishing TCP connection
        :param socket_keepalive: Whether to enable TCP Keepalive detection
        :param health_check_interval: health check interval (seconds)
        :param decode_responses: Whether to automatically decode the byte stream (bytes) returned by Redis into a string (utf-8)
        """
        super().__init__(
            host=host,
            port=port,
            password=password,
            db=db,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            socket_keepalive=socket_keepalive,
            health_check_interval=health_check_interval,
            decode_responses=decode_responses,
        )

    async def init(self) -> None:
        """Initialize Redis server"""
        try:
            await self.ping()
        except TimeoutError:
            log.error('Redis server connection timed out')
            sys.exit()
        except AuthenticationError:
            log.error('Redis server connection authentication failed')
            sys.exit()
        except Exception as e:
            log.error('Redis server connection exception {}', e)
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
