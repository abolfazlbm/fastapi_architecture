#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.task.model.result import TaskResult


class CRUDTaskResult(CRUDPlus[TaskResult]):
    """Task result database operation class"""

    async def get(self, db: AsyncSession, pk: int) -> TaskResult | None:
        """
        Get task results details

        :param db: database session
        :param pk: Task ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_list(self, name: str | None, task_id: str | None) -> Select:
        """
        Get a list of task results

        :param name: task name
        :param task_id: Task ID
        :return:
        """
        filters = {}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if task_id is not None:
            filters['task_id'] = task_id

        return await self.select_order('id', 'desc', **filters)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        Batch deletion of task results

        :param db: database session
        :param pks: Task result ID list
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


task_result_dao: CRUDTaskResult = CRUDTaskResult(TaskResult)
