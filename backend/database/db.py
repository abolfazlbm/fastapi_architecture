import sys

from collections.abc import AsyncGenerator, Mapping
from contextlib import AbstractAsyncContextManager
from functools import partial
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import URL, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.common.enums import DataBaseType
from backend.common.log import log
from backend.common.model import MappedBase
from backend.common.observability.prometheus.sqlalchemy import observe_sqlalchemy_pool_connections
from backend.core.conf import settings


def get_database_url(*, unittest: bool = False, with_database: bool = True) -> URL:
    """
    Create a database link

    :param unittest: whether to use for unit testing
    :param with_database: whether to include the database name (not required when creating the database)
    :return:
    """
    if with_database:
        database = settings.DATABASE_SCHEMA if not unittest else f'{settings.DATABASE_SCHEMA}_test'
    else:
        database = None if DataBaseType.mysql == settings.DATABASE_TYPE else 'postgres'

    url = URL.create(
        drivername='mysql+asyncmy' if DataBaseType.mysql == settings.DATABASE_TYPE else 'postgresql+asyncpg',
        username=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=database,
    )
    if DataBaseType.mysql == settings.DATABASE_TYPE and with_database:
        url = url.update_query_dict({'charset': settings.DATABASE_CHARSET})
    return url


def create_database_async_engine(url: str | URL) -> AsyncEngine:
    """
    Create a database asynchronous engine

    :param url: database connection address
    :return:
    """
    try:
        return create_async_engine(
            url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.DATABASE_POOL_ECHO,
            future=True,
            # Medium concurrency
            pool_size=10, # Low:- High:+
            max_overflow=20, # Low:- High:+
            pool_timeout=30, # Low: + High:-
            pool_recycle=3600, # Low: + High:-
            pool_pre_ping=True, # Low: False High: True
            pool_use_lifo=False, # Low: False High: True
        )
    except Exception as e:
        log.error(f'Database connection failed {e}')
        sys.exit()


class DatabaseAsyncSessionMaker:
    """按数据源名选择对应的 async_sessionmaker"""

    def __init__(self, makers: Mapping[str, async_sessionmaker[AsyncSession]]) -> None:
        if 'default' not in makers:
            raise ValueError('会话工厂必须包含 default 数据源')
        self._makers = dict(makers)

    def _get_maker(self, source: str) -> async_sessionmaker[AsyncSession]:
        """
        获取指定数据源的会话工厂

        :param source: 数据源名称
        :return:
        """
        try:
            return self._makers[source]
        except KeyError as e:
            raise ValueError(f'未知数据库数据源: {source}') from e

    def __call__(self, source: str = 'default', **kwargs: Any) -> AsyncSession:
        """
        创建数据库会话

        :param source: 数据源名称
        :return:
        """
        return self._get_maker(source)(**kwargs)

    def begin(self, source: str = 'default') -> AbstractAsyncContextManager[AsyncSession]:
        """
        创建会话并开启事务，退出时提交并关闭

        :param source: 数据源名称
        :return:
        """
        return self._get_maker(source).begin()


def create_database_async_session(
    async_engine: AsyncEngine,
    *,
    source_binds: Mapping[str, AsyncEngine] | None = None,
) -> DatabaseAsyncSessionMaker:
    """
    创建支持命名数据源的数据库异步会话

    :param async_engine: 默认数据源异步引擎
    :param source_binds: 额外数据源异步引擎
    :return:
    """
    engines = dict(source_binds or {})
    engines.setdefault('default', async_engine)
    return DatabaseAsyncSessionMaker({
        source: async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        for source, engine in engines.items()
    })


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取默认数据源会话"""
    async with async_db_session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """获取默认数据源事务会话"""
    async with async_db_session.begin() as session:
        yield session


async def create_tables() -> None:
    """Create a database table"""
    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all)


async def drop_tables() -> None:
    """Drop database table"""
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)


def uuid4_str() -> str:
    """Database Engine UUID Type Compatibility Solution"""
    return str(uuid4())


# SQLA Async Engines And Sessions
async_engine = create_database_async_engine(get_database_url())
_database_engines: dict[str, AsyncEngine] = {'default': async_engine}
for source, url in settings.DATABASE_SOURCES.items():
    if not source or source == 'default':
        raise ValueError('DATABASE_SOURCES 数据源名称不能为空且不能为 default')
    _database_engines[source] = create_database_async_engine(url)

async_db_session = create_database_async_session(async_engine, source_binds=_database_engines)


def get_database_engines() -> Mapping[str, AsyncEngine]:
    """获取所有数据库引擎"""
    return _database_engines


async def dispose_database() -> None:
    """释放所有数据库连接池"""
    for engine in _database_engines.values():
        await engine.dispose()


# SQLA Connection pool indicator monitoring
for source, engine in _database_engines.items():
    event.listen(
        engine.sync_engine.pool,
        'connect',
        partial(observe_sqlalchemy_pool_connections, pool=engine.sync_engine.pool, source=source),
    )
    event.listen(
        engine.sync_engine.pool,
        'checkout',
        partial(observe_sqlalchemy_pool_connections, pool=engine.sync_engine.pool, source=source),
    )
    event.listen(
        engine.sync_engine.pool,
        'checkin',
        partial(observe_sqlalchemy_pool_connections, pool=engine.sync_engine.pool, source=source),
    )

# Session Annotated
type CurrentSession = Annotated[AsyncSession, Depends(get_db)]
type CurrentSessionTransaction = Annotated[AsyncSession, Depends(get_db_transaction)]
