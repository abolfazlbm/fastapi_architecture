#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from typing import Sequence

from sqlalchemy import Select
from starlette.concurrency import run_in_threadpool

from backend.app.task.celery import celery_app
from backend.app.task.crud.crud_scheduler import task_scheduler_dao
from backend.app.task.enums import TaskSchedulerType
from backend.app.task.model import TaskScheduler
from backend.app.task.schema.scheduler import CreateTaskSchedulerParam, UpdateTaskSchedulerParam
from backend.app.task.utils.tzcrontab import crontab_verify
from backend.common.exception import errors
from backend.database.db import async_db_session


class TaskSchedulerService:
    """Task Scheduling Service Class"""

    @staticmethod
    async def get(*, pk) -> TaskScheduler | None:
        """
        Get task scheduling details

        :param pk: Task Scheduling ID
        :return:
        """
        async with async_db_session() as db:
            task_scheduler = await task_scheduler_dao.get(db, pk)
            if not task_scheduler:
                raise errors.NotFoundError(msg='Task Scheduling does not exist')
            return task_scheduler

    @staticmethod
    async def get_all() -> Sequence[TaskScheduler]:
        """Get all task schedules"""
        async with async_db_session() as db:
            task_schedulers = await task_scheduler_dao.get_all(db)
            return task_schedulers

    @staticmethod
    async def get_select(*, name: str | None, type: int | None) -> Select:
        """
        Get the task schedule list query conditions

        :param name: task scheduling name
        :param type: Task scheduling type
        :return:
        """
        return await task_scheduler_dao.get_list(name=name, type=type)

    @staticmethod
    async def create(*, obj: CreateTaskSchedulerParam) -> None:
        """
        Create a task schedule

        :param obj: Task Scheduling Create Parameters
        :return:
        """
        async with async_db_session.begin() as db:
            task_scheduler = await task_scheduler_dao.get_by_name(db, obj.name)
            if task_scheduler:
                raise errors.ConflictError(msg='Task Scheduling Already Exist')
            if obj.type == TaskSchedulerType.CRONTAB:
                crontab_verify(obj.crontab)
            await task_scheduler_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateTaskSchedulerParam) -> int:
        """
        Update task schedule

        :param pk: Task Scheduling ID
        :param obj: Task Scheduling Update Parameters
        :return:
        """
        async with async_db_session.begin() as db:
            task_scheduler = await task_scheduler_dao.get(db, pk)
            if not task_scheduler:
                raise errors.NotFoundError(msg='Task Scheduling does not exist')
            if task_scheduler.name != obj.name:
                if await task_scheduler_dao.get_by_name(db, obj.name):
                    raise errors.ConflictError(msg='Task Scheduling Already Exist')
            if task_scheduler.type == TaskSchedulerType.CRONTAB:
                crontab_verify(obj.crontab)
            count = await task_scheduler_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def update_status(*, pk: int) -> int:
        """
        Update task scheduling status

        :param pk: Task Scheduling ID
        :return:
        """
        async with async_db_session.begin() as db:
            task_scheduler = await task_scheduler_dao.get(db, pk)
            if not task_scheduler:
                raise errors.NotFoundError(msg='Task Scheduling does not exist')
            count = await task_scheduler_dao.set_status(db, pk, not task_scheduler.enabled)
            return count

    @staticmethod
    async def delete(*, pk) -> int:
        """
        Delete task schedule

        :param pk: User ID
        :return:
        """
        async with async_db_session.begin() as db:
            task_scheduler = await task_scheduler_dao.get(db, pk)
            if not task_scheduler:
                raise errors.NotFoundError(msg='Task Scheduling does not exist')
            count = await task_scheduler_dao.delete(db, pk)
            return count

    @staticmethod
    async def execute(*, pk: int) -> None:
        """
        Perform tasks

        :param pk: Task Scheduling ID
        :return:
        """
        async with async_db_session() as db:
            workers = await run_in_threadpool(celery_app.control.ping, timeout=0.5)
            if not workers:
                raise errors.ServerError(msg='Celery Worker is not available yet, please try again later')
            task_scheduler = await task_scheduler_dao.get(db, pk)
            if not task_scheduler:
                raise errors.NotFoundError(msg='Task Scheduling does not exist')
            try:
                args = json.loads(task_scheduler.args) if task_scheduler.args else None
                kwargs = json.loads(task_scheduler.kwargs) if task_scheduler.kwargs else None
            except (TypeError, json.JSONDecodeError):
                raise errors.RequestError(msg='Execution failed, task parameters are illegal')
            else:
                celery_app.send_task(name=task_scheduler.task, args=args, kwargs=kwargs)


task_scheduler_service: TaskSchedulerService = TaskSchedulerService()
