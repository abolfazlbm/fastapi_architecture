import sys

from collections.abc import AsyncGenerator
from functools import partial
from typing import Annotated, Any, TypeAlias
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


def create_database_async_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession | Any]:
    """
    Create a database asynchronous session

    :param engine: database asynchronous engine
    :return:
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,  # Disable automatic refresh
        expire_on_commit=False, # Disable expiration of commit
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_db_session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with a transaction"""
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
async_db_session = create_database_async_session(async_engine)

# SQLA Connection pool indicator monitoring
event.listen(
    async_engine.sync_engine.pool,
    'connect',
    partial(observe_sqlalchemy_pool_connections, pool=async_engine.sync_engine.pool),
)
event.listen(
    async_engine.sync_engine.pool,
    'checkout',
    partial(observe_sqlalchemy_pool_connections, pool=async_engine.sync_engine.pool),
)
event.listen(
    async_engine.sync_engine.pool,
    'checkin',
    partial(observe_sqlalchemy_pool_connections, pool=async_engine.sync_engine.pool),
)

# Session Annotated
CurrentSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]
CurrentSessionTransaction: TypeAlias = Annotated[AsyncSession, Depends(get_db_transaction)]
