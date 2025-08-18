#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import Dept
from backend.app.admin.schema.dept import CreateDeptParam, UpdateDeptParam
from backend.common.security.permission import filter_data_permission


class CRUDDept(CRUDPlus[Dept]):
    """Departmental Database Operation Class"""

    async def get(self, db: AsyncSession, dept_id: int) -> Dept | None:
        """
        Get department details

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.select_model_by_column(db, id=dept_id, del_flag=0)

    async def get_by_name(self, db: AsyncSession, name: str) -> Dept | None:
        """
        Get department by name

        :param db: database session
        :param name: department name
        :return:
        """
        return await self.select_model_by_column(db, name=name, del_flag=0)

    async def get_all(
        self,
        request: Request,
        db: AsyncSession,
        name: str | None,
        leader: str | None,
        phone: str | None,
        status: int | None,
    ) -> Sequence[Dept]:
        """
        Get all departments

        :param request: FastAPI request object
        :param db: database session
        :param name: department name
        :param leader: person in charge
        :param phone: Contact number
        :param status: department status
        :return:
        """
        filters = {'del_flag': 0}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if leader is not None:
            filters['leader__like'] = f'%{leader}%'
        if phone is not None:
            filters['phone__startswith'] = phone
        if status is not None:
            filters['status'] = status

        data_filtered = await filter_data_permission(db, request)
        return await self.select_models_order(db, 'sort', 'desc', data_filtered, **filters)

    async def create(self, db: AsyncSession, obj: CreateDeptParam) -> None:
        """
        Create a department

        :param db: database session
        :param obj: Create department parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, dept_id: int, obj: UpdateDeptParam) -> int:
        """
        Update department

        :param db: database session
        :param dept_id: Department ID
        :param obj: Update department parameters
        :return:
        """
        return await self.update_model(db, dept_id, obj)

    async def delete(self, db: AsyncSession, dept_id: int) -> int:
        """
        Delete the department

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.delete_model_by_column(db, id=dept_id, logical_deletion=True, deleted_flag_column='del_flag')

    async def get_with_relation(self, db: AsyncSession, dept_id: int) -> Dept | None:
        """
        Obtain department and related data

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.select_model(db, dept_id, load_strategies=['users'])

    async def get_children(self, db: AsyncSession, dept_id: int) -> Sequence[Dept | None]:
        """
        Get a list of sub-departments

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.select_models(db, parent_id=dept_id, del_flag=0)

dept_dao: CRUDDept = CRUDDept(Dept)
