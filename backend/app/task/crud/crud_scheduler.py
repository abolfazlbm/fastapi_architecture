#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.task.model import TaskScheduler
from backend.app.task.schema.scheduler import CreateTaskSchedulerParam, UpdateTaskSchedulerParam


class CRUDTaskScheduler(CRUDPlus[TaskScheduler]):
    """Task Scheduling Database Operation Class"""

    @staticmethod
    async def get(db: AsyncSession, pk: int) -> TaskScheduler | None:
        """
        Get task schedule

        :param db: database session
        :param pk: Task Scheduling ID
        :return:
        """
        return await task_scheduler_dao.select_model(db, pk)

    async def get_all(self, db: AsyncSession) -> Sequence[TaskScheduler]:
        """
        Get all task schedules

        :param db: database session
        :return:
        """
        return await self.select_models(db)

    async def get_list(self, name: str | None, type: int | None) -> Select:
        """
        Get the task schedule list

        :param name: task scheduling name
        :param type: Task scheduling type
        :return:
        """
        filters = {}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if type is not None:
            filters['type'] = type

        return await self.select_order('id', **filters)

    async def get_by_name(self, db: AsyncSession, name: str) -> TaskScheduler | None:
        """
        Get task schedule by name

        :param db: database session
        :param name: task scheduling name
        :return:
        """
        return await self.select_model_by_column(db, name=name)

    async def create(self, db: AsyncSession, obj: CreateTaskSchedulerParam) -> None:
        """
        Create a task schedule

        :param db: database session
        :param obj: Create task scheduling parameters
        :return:
        """
        await self.create_model(db, obj, flush=True)
        TaskScheduler.no_changes = False

    async def update(self, db: AsyncSession, pk: int, obj: UpdateTaskSchedulerParam) -> int:
        """
        Update task schedule

        :param db: database session
        :param pk: Task Scheduling ID
        :param obj: Update task scheduling parameters
        :return:
        """
        task_scheduler = await self.get(db, pk)
        for key, value in obj.model_dump(exclude_unset=True).items():
            setattr(task_scheduler, key, value)
        TaskScheduler.no_changes = False
        return 1

    async def set_status(self, db: AsyncSession, pk: int, status: bool) -> int:
        """
        Set task scheduling status

        :param db: database session
        :param pk: Task Scheduling ID
        :param status: status
        :return:
        """
        task_scheduler = await self.get(db, pk)
        setattr(task_scheduler, 'enabled', status)
        TaskScheduler.no_changes = False
        return 1

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """
        Delete task schedule

        :param db: database session
        :param pk: Task Scheduling ID
        :return:
        """
        task_scheduler = await self.get(db, pk)
        await db.delete(task_scheduler)
        TaskScheduler.no_changes = False
        return 1


task_scheduler_dao: CRUDTaskScheduler = CRUDTaskScheduler(TaskScheduler)
