from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.config.model import Config
from backend.plugin.config.schema.config import CreateConfigParam, UpdateConfigParam
from backend.utils.timezone import timezone


class CRUDConfig(CRUDPlus[Config]):
    """System parameter parameter configuration database operation class"""

    async def get(self, db: AsyncSession, pk: int) -> Config | None:
        """
        Get parameter configuration details

        :param db: database session
        :param pk: parameter configuration ID
        :return:
        """
        return await self.select_model_by_column(db, id=pk, deleted=0)

    async def get_all(self, db: AsyncSession, type: str | None) -> Sequence[Config | None]:
        """
        Get parameter configuration by key name

        :param db: database session
        :param type: parameter configuration type
        :return:
        """
        filters = {'deleted': 0}

        if type is not None:
            filters['type'] = type

        return await self.select_models(db, **filters)

    async def get_all_by_ids(self, db: AsyncSession, pks: list[int]) -> Sequence[Config]:
        """
        通过 ID 列表批量获取参数配置

        :param db: 数据库会话
        :param pks: 参数配置 ID 列表
        :return:
        """
        return await self.select_models(db, id__in=pks, deleted=0)

    async def get_all_by_keys(self, db: AsyncSession, keys: list[str]) -> Sequence[Config]:
        """
        通过键名列表批量获取参数配置

        :param db: 数据库会话
        :param keys: 参数配置键名列表
        :return:
        """
        return await self.select_models(db, key__in=keys, deleted=0)

    async def get_by_key(self, db: AsyncSession, key: str) -> Config | None:
        """
        Get parameter configuration by key name

        :param db: database session
        :param key: Parameter configuration key name
        :return:
        """
        return await self.select_model_by_column(db, key=key, deleted=0)

    async def get_select(self, name: str | None, type: str | None) -> Select:
        """
        Get parameter configuration list query expression

        :param name: Parameter configuration name
        :param type: parameter configuration type
        :return:
        """
        filters = {'deleted': 0}

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
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

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
        return await self.delete_model_by_column(
            db,
            allow_multiple=True,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id__in=pks,
            deleted=0,
        )


config_dao: CRUDConfig = CRUDConfig(Config)
