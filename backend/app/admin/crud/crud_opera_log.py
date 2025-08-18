#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import OperaLog
from backend.app.admin.schema.opera_log import CreateOperaLogParam


class CRUDOperaLogDao(CRUDPlus[OperaLog]):
    """Operation log database operation class"""

    async def get_list(self, username: str | None, status: int | None, ip: str | None) -> Select:
        """
        Get the operation log list

        :param username: Username
        :param status: operation status
        :param ip: IP address
        :return:
        """
        filters = {}

        if username is not None:
            filters['username__like'] = f'%{username}%'
        if status is not None:
            filters['status__eq'] = status
        if ip is not None:
            filters['ip__like'] = f'%{ip}%'

        return await self.select_order('created_time', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateOperaLogParam) -> None:
        """
        Create an operation log

        :param db: database session
        :param obj: Operation log creation parameters
        :return:
        """
        await self.create_model(db, obj)

    async def bulk_create(self, db: AsyncSession, objs: list[CreateOperaLogParam]) -> None:
        """
        Bulk creation of operation logs

        :param db: database session
        :param objs: operation log creation parameter list
        :return:
        """
        await self.create_models(db, objs)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        Batch delete operation log

        :param db: database session
        :param pks: Operation log ID list
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    @staticmethod
    async def delete_all(db: AsyncSession) -> None:
        """
        Delete all logs

        :param db: database session
        :return:
        """
        await db.execute(sa_delete(OperaLog))


opera_log_dao: CRUDOperaLogDao = CRUDOperaLogDao(OperaLog)
