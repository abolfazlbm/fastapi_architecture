from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.crud.crud_data_rule import data_rule_dao
from backend.app.admin.crud.crud_data_scope import data_scope_dao
from backend.app.admin.model import DataScope
from backend.app.admin.schema.data_scope import (
    CreateDataScopeParam,
    DeleteDataScopeParam,
    UpdateDataScopeParam,
    UpdateDataScopeRuleParam,
)
from backend.app.admin.utils.cache import user_cache_manager
from backend.common.exception import errors
from backend.common.pagination import paging_data


class DataScopeService:
    """Data scope service class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> DataScope:
        """
        Get data range details

        :param db: database session
        :param pk: Range ID
        :return:
        """

        data_scope = await data_scope_dao.get(db, pk)
        if not data_scope:
            raise errors.NotFoundError(msg='Data range does not exist')
        return data_scope

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[DataScope]:
        """
        Get all data ranges

        :param db: database session
        :return:
        """

        data_scopes = await data_scope_dao.get_all(db)
        return data_scopes

    @staticmethod
    async def get_rules(*, db: AsyncSession, pk: int) -> DataScope:
        """
        Get data range rules

        :param db: database session
        :param pk: Range ID
        :return:
        """

        data_scope = await data_scope_dao.get_join(db, pk)
        if not data_scope:
            raise errors.NotFoundError(msg='Data range does not exist')
        return data_scope

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None, status: int | None) -> dict[str, Any]:
        """
        Get a list of data ranges

        :param db: database session
        :param name: range name
        :param status: range status
        :return:
        """
        data_scope_select = await data_scope_dao.get_select(name, status)
        return await paging_data(db, data_scope_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDataScopeParam) -> None:
        """
        Create data range

        :param db: database session
        :param obj: Data range parameters
        :return:
        """
        data_scope = await data_scope_dao.get_by_name(db, obj.name)
        if data_scope:
            raise errors.ConflictError(msg='The data range already exists')
        await data_scope_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDataScopeParam) -> int:
        """
        Update data range

        :param db: database session
        :param pk: Range ID
        :param obj: Data range update parameters
        :return:
        """
        data_scope = await data_scope_dao.get(db, pk)
        if not data_scope:
            raise errors.NotFoundError(msg='Data range does not exist')
        if data_scope.name != obj.name and await data_scope_dao.get_by_name(db, obj.name):
            raise errors.ConflictError(msg='Data range already exists')
        count = await data_scope_dao.update(db, pk, obj)
        await user_cache_manager.clear_by_data_scope_id(db, [pk])
        return count

    @staticmethod
    async def update_data_scope_rule(*, db: AsyncSession, pk: int, rule_ids: UpdateDataScopeRuleParam) -> int:
        """
        Update data scope rules

        :param db: database session
        :param pk: Range ID
        :param rule_ids: Rule ID list
        :return:
        """
        data_scope = await data_scope_dao.get(db, pk)
        if not data_scope:
            raise errors.NotFoundError(msg='Data range does not exist')
        for rule_id in rule_ids.rules:
            rule = await data_rule_dao.get(db, rule_id)
            if not rule:
                raise errors.NotFoundError(msg='Data rule does not exist')
        count = await data_scope_dao.update_rules(db, pk, rule_ids)
        await user_cache_manager.clear_by_data_scope_id(db, [pk])
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteDataScopeParam) -> int:
        """
        Batch delete data range

        :param db: database session
        :param obj: Range ID List
        :return:
        """
        count = await data_scope_dao.delete(db, obj.pks)
        await user_cache_manager.clear_by_data_scope_id(db, obj.pks)
        return count


data_scope_service: DataScopeService = DataScopeService()
