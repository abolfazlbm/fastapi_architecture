from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.config.crud.crud_config import config_dao
from backend.plugin.config.model import Config
from backend.plugin.config.schema.config import (
    CreateConfigParam,
    UpdateConfigParam,
    UpdateConfigsParam,
)


class ConfigService:
    """Parameter configuration service class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Config:
        """
        Get parameter configuration details

        :param db: database session
        :param pk: parameter configuration ID
        :return:
        """

        config = await config_dao.get(db, pk)
        if not config:
            raise errors.NotFoundError(msg='Parameter configuration does not exist')
        return config

    @staticmethod
    async def get_all(*, db: AsyncSession, type: str | None) -> Sequence[Config | None]:
        """
        Get all parameter configurations

        :param db: database session
        :param type: parameter configuration type
        :return:
        """

        return await config_dao.get_all(db, type)

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None, type: str | None) -> dict[str, Any]:
        """
        Get parameter configuration list

        :param db: database session
        :param name: Parameter configuration name
        :param type: parameter configuration type
        :return:
        """
        config_select = await config_dao.get_select(name=name, type=type)
        return await paging_data(db, config_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateConfigParam) -> None:
        """
        Create parameter configuration

        :param db: database session
        :param obj: Parameter configuration creation parameters
        :return:
        """

        config = await config_dao.get_by_key(db, obj.key)
        if config:
            raise errors.ConflictError(msg=f'parameter configuration {obj.key} already exists')
        await config_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateConfigParam) -> int:
        """
        Update parameter configuration

        :param db: database session
        :param pk: parameter configuration ID
        :param obj: Parameter configuration update parameters
        :return:
        """

        config = await config_dao.get(db, pk)
        if not config:
            raise errors.NotFoundError(msg='Parameter configuration does not exist')
        if config.key != obj.key:
            config = await config_dao.get_by_key(db, obj.key)
            if config:
                raise errors.ConflictError(msg=f'parameter configuration {obj.key} already exists')
        count = await config_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def bulk_update(*, db: AsyncSession, objs: list[UpdateConfigsParam]) -> int:
        """
        Batch update parameter configuration

        :param db: database session
        :param objs: parameter configuration batch update parameters
        :return:
        """

        for _batch in range(0, len(objs), 1000):
            for obj in objs:
                config = await config_dao.get(db, obj.id)
                if not config:
                    raise errors.NotFoundError(msg='Parameter configuration does not exist')
                if config.key != obj.key:
                    config = await config_dao.get_by_key(db, obj.key)
                    if config:
                        raise errors.ConflictError(msg=f'parameter configuration {obj.key} already exists')
        count = await config_dao.bulk_update(db, objs)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, pks: list[int]) -> int:
        """
        Delete parameter configurations in batches

        :param db: database session
        :param pks: parameter configuration ID list
        :return:
        """

        count = await config_dao.delete(db, pks)
        return count


config_service: ConfigService = ConfigService()
