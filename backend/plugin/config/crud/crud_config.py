from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.config.model import Config
from backend.plugin.config.schema.config import CreateConfigParam, UpdateConfigParam


class CRUDConfig(CRUDPlus[Config]):
    """System parameter parameter configuration database operation class"""

    async def get(self, db: AsyncSession, pk: int) -> Config | None:
        """
        Get parameter configuration details

        :param db: database session
        :param pk: parameter configuration ID
        :return:
        """
        return await self.select_model_by_column(db, id=pk)

    async def get_all(self, db: AsyncSession, type: str) -> Sequence[Config | None]:
        """
        Get parameter configuration by key name

        :param db: database session
        :param type: parameter configuration type
        :return:
        """
        return await self.select_models(db, type=type)

    async def get_by_key(self, db: AsyncSession, key: str) -> Config | None:
        """
        Get parameter configuration by key name

        :param db: database session
        :param key: Parameter configuration key name
        :return:
        """
        return await self.select_model_by_column(db, key=key)

    async def get_select(self, name: str | None, type: str | None) -> Select:
        """
        Get parameter configuration list query expression

        :param name: Parameter configuration name
        :param type: parameter configuration type
        :return:
        """
        filters = {}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if type is not None:
            filters['type__like'] = f'%{type}%'

        return await self.select_order('created_time', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateConfigParam) -> None:
        """
        Create parameter configuration

        :param db: database session
        :param obj: Create parameter configuration parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateConfigParam) -> int:
        """
        Update parameter configuration

        :param db: database session
        :param pk: parameter configuration ID
        :param obj: Update parameter configuration parameters
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def bulk_update(self, db: AsyncSession, objs: list[UpdateConfigParam]) -> int:
        """
        Batch update parameter configuration

        :param db: database session
        :param objs: Batch update parameter configuration parameters
        :return:
        """
        return await self.bulk_update_models(db, objs)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        Delete parameter configurations in batches

        :param db: database session
        :param pks: parameter configuration ID list
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


config_dao: CRUDConfig = CRUDConfig(Config)
