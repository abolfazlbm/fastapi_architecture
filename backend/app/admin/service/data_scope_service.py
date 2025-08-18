#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select

from backend.app.admin.crud.crud_data_scope import data_scope_dao
from backend.app.admin.model import DataScope
from backend.app.admin.schema.data_scope import (
    CreateDataScopeParam,
    DeleteDataScopeParam,
    UpdateDataScopeParam,
    UpdateDataScopeRuleParam,
)
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client


class DataScopeService:
    """Data scope service class"""

    @staticmethod
    async def get(*, pk: int) -> DataScope:
        """
        Get data range details

        :param pk: Range ID
        :return:
        """
        async with async_db_session() as db:
            data_scope = await data_scope_dao.get(db, pk)
            if not data_scope:
                raise errors.NotFoundError(msg='Data range does not exist')
            return data_scope

    @staticmethod
    async def get_all() -> Sequence[DataScope]:
        """Get all data ranges"""
        async with async_db_session() as db:
            data_scopes = await data_scope_dao.get_all(db)
            return data_scopes

    @staticmethod
    async def get_rules(*, pk: int) -> DataScope:
        """
        Get data range rules

        :param pk: Range ID
        :return:
        """
        async with async_db_session() as db:
            data_scope = await data_scope_dao.get_with_relation(db, pk)
            if not data_scope:
                raise errors.NotFoundError(msg='Data range does not exist')
            return data_scope

    @staticmethod
    async def get_select(*, name: str | None, status: int | None) -> Select:
        """
        Get the query conditions for data range list

        :param name: range name
        :param status: range status
        :return:
        """
        return await data_scope_dao.get_list(name, status)

    @staticmethod
    async def create(*, obj: CreateDataScopeParam) -> None:
        """
        Create data range

        :param obj: Data range parameters
        :return:
        """
        async with async_db_session.begin() as db:
            data_scope = await data_scope_dao.get_by_name(db, obj.name)
            if data_scope:
                raise errors.ConflictError(msg='The data range already exists')
            await data_scope_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateDataScopeParam) -> int:
        """
        Update data range

        :param pk: Range ID
        :param obj: Data range update parameters
        :return:
        """
        async with async_db_session.begin() as db:
            data_scope = await data_scope_dao.get(db, pk)
            if not data_scope:
                raise errors.NotFoundError(msg='Data range does not exist')
            if data_scope.name != obj.name:
                if await data_scope_dao.get_by_name(db, obj.name):
                    raise errors.ConflictError(msg='Data range already exists')
            count = await data_scope_dao.update(db, pk, obj)
            for role in await data_scope.awaitable_attrs.roles:
                for user in await role.awaitable_attrs.users:
                    await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_data_scope_rule(*, pk: int, rule_ids: UpdateDataScopeRuleParam) -> int:
        """
        Update data scope rules

        :param pk: Range ID
        :param rule_ids: Rule ID list
        :return:
        """
        async with async_db_session.begin() as db:
            count = await data_scope_dao.update_rules(db, pk, rule_ids)
            return count

    @staticmethod
    async def delete(*, obj: DeleteDataScopeParam) -> int:
        """
        Batch delete data range

        :param obj: Range ID List
        :return:
        """
        async with async_db_session.begin() as db:
            count = await data_scope_dao.delete(db, obj.pks)
            for pk in obj.pks:
                data_rule = await data_scope_dao.get(db, pk)
                if data_rule:
                    for role in await data_rule.awaitable_attrs.roles:
                        for user in await role.awaitable_attrs.users:
                            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count


data_scope_service: DataScopeService = DataScopeService()
