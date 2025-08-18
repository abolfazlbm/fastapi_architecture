#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Sequence

from sqlalchemy import Select

from backend.app.admin.crud.crud_data_scope import data_scope_dao
from backend.app.admin.crud.crud_menu import menu_dao
from backend.app.admin.crud.crud_role import role_dao
from backend.app.admin.model import Role
from backend.app.admin.schema.role import (
    CreateRoleParam,
    DeleteRoleParam,
    UpdateRoleMenuParam,
    UpdateRoleParam,
    UpdateRoleScopeParam,
)
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client
from backend.utils.build_tree import get_tree_data


class RoleService:
    """Role Service Class"""

    @staticmethod
    async def get(*, pk: int) -> Role:
        """
        Get character details

        :param pk: role ID
        :return:
        """
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            return role

    @staticmethod
    async def get_all() -> Sequence[Role]:
        """Get all roles"""
        async with async_db_session() as db:
            roles = await role_dao.get_all(db)
            return roles

    @staticmethod
    async def get_select(*, name: str | None, status: int | None) -> Select:
        """
        Get the character list query criteria

        :param name: role name
        :param status: status
        :return:
        """
        return await role_dao.get_list(name=name, status=status)

    @staticmethod
    async def get_menu_tree(*, pk: int) -> list[dict[str, Any] | None]:
        """
        Get the menu tree structure of the character

        :param pk: role ID
        :return:
        """
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            menu_tree = get_tree_data(role.menus) if role.menus else []
            return menu_tree

    @staticmethod
    async def get_scopes(*, pk: int) -> list[int]:
        """
        Get the list of role data ranges

        :param pk:
        :return:
        """
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            scope_ids = [scope.id for scope in role.scopes]
            return scope_ids

    @staticmethod
    async def create(*, obj: CreateRoleParam) -> None:
        """
        Create a role

        :param obj: role creation parameters
        :return:
        """
        async with async_db_session.begin() as db:
            role = await role_dao.get_by_name(db, obj.name)
            if role:
                raise errors.ConflictError(msg='role already exists')
            await role_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateRoleParam) -> int:
        """
        Update roles

        :param pk: role ID
        :param obj: role update parameters
        :return:
        """
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            if role.name != obj.name:
                if await role_dao.get_by_name(db, obj.name):
                    raise errors.ConflictError(msg='role already exists')
            count = await role_dao.update(db, pk, obj)
            for user in await role.awaitable_attrs.users:
                await redis_client.delete_prefix(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_role_menu(*, pk: int, menu_ids: UpdateRoleMenuParam) -> int:
        """
        Update the role menu

        :param pk: role ID
        :param menu_ids: Menu ID List
        :return:
        """
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            for menu_id in menu_ids.menus:
                menu = await menu_dao.get(db, menu_id)
                if not menu:
                    raise errors.NotFoundError(msg='menu does not exist')
            count = await role_dao.update_menus(db, pk, menu_ids)
            for user in await role.awaitable_attrs.users:
                await redis_client.delete_prefix(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_role_scope(*, pk: int, scope_ids: UpdateRoleScopeParam) -> int:
        """
        Update role data range

        :param pk: role ID
        :param scope_ids: Permission Rule ID List
        :return:
        """
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg='role does not exist')
            for scope_id in scope_ids.scopes:
                scope = await data_scope_dao.get(db, scope_id)
                if not scope:
                    raise errors.NotFoundError(msg='Data range does not exist')
            count = await role_dao.update_scopes(db, pk, scope_ids)
            for user in await role.awaitable_attrs.users:
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def delete(*, obj: DeleteRoleParam) -> int:
        """
        Batch delete roles

        :param obj: Role ID list
        :return:
        """
        async with async_db_session.begin() as db:
            count = await role_dao.delete(db, obj.pks)
            for pk in obj.pks:
                role = await role_dao.get(db, pk)
                if role:
                    for user in await role.awaitable_attrs.users:
                        await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count


role_service: RoleService = RoleService()
