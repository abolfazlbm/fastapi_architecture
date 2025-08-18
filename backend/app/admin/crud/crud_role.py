#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import DataScope, Menu, Role
from backend.app.admin.schema.role import (
    CreateRoleParam,
    UpdateRoleMenuParam,
    UpdateRoleParam,
    UpdateRoleScopeParam,
)


class CRUDRole(CRUDPlus[Role]):
    """Role database operation class"""

    async def get(self, db: AsyncSession, role_id: int) -> Role | None:
        """
        Get character details

        :param db: database session
        :param role_id: Role ID
        :return:
        """
        return await self.select_model(db, role_id)

    async def get_with_relation(self, db: AsyncSession, role_id: int) -> Role | None:
        """
        Get roles and associated data

        :param db: database session
        :param role_id: Role ID
        :return:
        """
        return await self.select_model(db, role_id, load_strategies=['menus', 'scopes'])

    async def get_all(self, db: AsyncSession) -> Sequence[Role]:
        """
        Get all roles

        :param db: database session
        :return:
        """
        return await self.select_models(db)

    async def get_list(self, name: str | None, status: int | None) -> Select:
        """
        Get the role list

        :param name: role name
        :param status: character status
        :return:
        """
        filters = {}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if status is not None:
            filters['status'] = status

        return await self.select_order(
            'id',
            load_strategies={
                'users': 'noload',
                'menus': 'noload',
                'scopes': 'noload',
            },
            **filters,
        )

    async def get_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """
        Get roles by name

        :param db: database session
        :param name: role name
        :return:
        """
        return await self.select_model_by_column(db, name=name)

    async def create(self, db: AsyncSession, obj: CreateRoleParam) -> None:
        """
        Create a role

        :param db: database session
        :param obj: Create role parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, role_id: int, obj: UpdateRoleParam) -> int:
        """
        Update roles

        :param db: database session
        :param role_id: Role ID
        :param obj: Update role parameters
        :return:
        """
        return await self.update_model(db, role_id, obj)

    async def update_menus(self, db: AsyncSession, role_id: int, menu_ids: UpdateRoleMenuParam) -> int:
        """
        Update the role menu

        :param db: database session
        :param role_id: Role ID
        :param menu_ids: Menu ID List
        :return:
        """
        current_role = await self.get_with_relation(db, role_id)
        stmt = select(Menu).where(Menu.id.in_(menu_ids.menus))
        menus = await db.execute(stmt)
        current_role.menus = menus.scalars().all()
        return len(current_role.menus)

    async def update_scopes(self, db: AsyncSession, role_id: int, scope_ids: UpdateRoleScopeParam) -> int:
        """
        Update role data range

        :param db: database session
        :param role_id: Role ID
        :param scope_ids: Permission scope ID list
        :return:
        """
        current_role = await self.get_with_relation(db, role_id)
        stmt = select(DataScope).where(DataScope.id.in_(scope_ids.scopes))
        scopes = await db.execute(stmt)
        current_role.scopes = scopes.scalars().all()
        return len(current_role.scopes)

    async def delete(self, db: AsyncSession, role_ids: list[int]) -> int:
        """
        Batch delete roles

        :param db: database session
        :param role_ids: Role ID list
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=role_ids)


role_dao: CRUDRole = CRUDRole(Role)
