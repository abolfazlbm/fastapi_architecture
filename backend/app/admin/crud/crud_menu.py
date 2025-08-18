#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import Menu
from backend.app.admin.schema.menu import CreateMenuParam, UpdateMenuParam


class CRUDMenu(CRUDPlus[Menu]):
    """Menu Database Operation Class"""

    async def get(self, db: AsyncSession, menu_id: int) -> Menu | None:
        """
        Get menu details

        :param db: database session
        :param menu_id: menu ID
        :return:
        """
        return await self.select_model(db, menu_id)

    async def get_by_title(self, db: AsyncSession, title: str) -> Menu | None:
        """
        Get menu by title

        :param db: database session
        :param title: menu title
        :return:
        """
        return await self.select_model_by_column(db, title=title, type__ne=2)

    async def get_all(self, db: AsyncSession, title: str | None, status: int | None) -> Sequence[Menu]:
        """
        Get menu list

        :param db: database session
        :param title: menu title
        :param status: menu status
        :return:
        """
        filters = {}

        if title is not None:
            filters['title__like'] = f'%{title}%'
        if status is not None:
            filters['status'] = status

        return await self.select_models_order(db, 'sort', **filters)

    async def get_sidebar(self, db: AsyncSession, menu_ids: list[int] | None) -> Sequence[Menu]:
        """
        Get the user's menu sidebar

        :param db: database session
        :param menu_ids: Menu ID List
        :return:
        """
        filters = {'type__in': [0, 1, 3, 4]}

        if menu_ids:
            filters['id__in'] = menu_ids

        return await self.select_models_order(db, 'sort', 'asc', **filters)

    async def create(self, db: AsyncSession, obj: CreateMenuParam) -> None:
        """
        Create menu

        :param db: database session
        :param obj: Create menu parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, menu_id: int, obj: UpdateMenuParam) -> int:
        """
        Update menu

        :param db: database session
        :param menu_id: menu ID
        :param obj: Update menu parameters
        :return:
        """
        return await self.update_model(db, menu_id, obj)

    async def delete(self, db: AsyncSession, menu_id: int) -> int:
        """
        Delete menu

        :param db: database session
        :param menu_id: menu ID
        :return:
        """
        return await self.delete_model(db, menu_id)

    async def get_children(self, db: AsyncSession, menu_id: int) -> list[Menu | None]:
        """
        Get a list of submenu

        :param db: database session
        :param menu_id: menu ID
        :return:
        """
        menu = await self.select_model(db, menu_id, load_strategies=['children'])
        return menu.children


menu_dao: CRUDMenu = CRUDMenu(Menu)
