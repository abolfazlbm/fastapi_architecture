#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from backend.common.log import log
from backend.core.conf import settings


class RedisCli(Redis):
    """Redis Client"""

    def __init__(self) -> None:
        """Initialize Redis Client"""
        super(RedisCli, self).__init__(
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

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None) -> None:
        """
        Delete all keys of the specified prefix

        :param prefix: prefix
        :param exclude: Excluded key
        :return:
        """
        keys = []
        async for key in self.scan_iter(match=f'{prefix}*'):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        if keys:
            await self.delete(*keys)


# Create a redis client singleton
redis_client: RedisCli = RedisCli()
