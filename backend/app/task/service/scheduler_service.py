import json

from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from backend.app.task.celery import celery_app
from backend.app.task.crud.crud_scheduler import task_scheduler_dao
from backend.app.task.enums import TaskSchedulerType
from backend.app.task.model import TaskScheduler
from backend.app.task.schema.scheduler import CreateTaskSchedulerParam, UpdateTaskSchedulerParam
from backend.app.task.utils.tzcrontab import crontab_verify
from backend.common.exception import errors
from backend.common.pagination import paging_data


class TaskSchedulerService:
    """Task Scheduling Service Class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> TaskScheduler | None:
        """
        Get task scheduling details

        :param db: database session
        :param pk: Task Scheduling ID
        :return:
        """

        task_scheduler = await task_scheduler_dao.get(db, pk)
        if not task_scheduler:
            raise errors.NotFoundError(msg='Task Scheduling does not exist')
        return task_scheduler

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[TaskScheduler]:
        """
        Get all task schedules

        :param db: database session
        :return:
        """

        task_schedulers = await task_scheduler_dao.get_all(db)
        return task_schedulers

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None, type: int | None) -> dict[str, Any]:
        """
        Get task schedule list

        :param db: database session
        :param name: task scheduling name
        :param type: Task scheduling type
        :return:
        """
        task_scheduler_select = await task_scheduler_dao.get_select(name=name, type=type)
        return await paging_data(db, task_scheduler_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateTaskSchedulerParam) -> None:
        """
        Create a task schedule

        :param db: database session
        :param obj: Task Scheduling Create Parameters
        :return:
        """

        task_scheduler = await task_scheduler_dao.get_by_name(db, obj.name)
        if task_scheduler:
            raise errors.ConflictError(msg='Task Scheduling Already Exist')
        if obj.type == TaskSchedulerType.CRONTAB:
            crontab_verify(obj.crontab)
        await task_scheduler_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateTaskSchedulerParam) -> int:
        """
        Update task schedule

        :param db: database session
        :param pk: Task Scheduling ID
        :param obj: Task Scheduling Update Parameters
        :return:
        """

        task_scheduler = await task_scheduler_dao.get(db, pk)
        if not task_scheduler:
            raise errors.NotFoundError(msg='Task Scheduling does not exist')
        if task_scheduler.name != obj.name and await task_scheduler_dao.get_by_name(db, obj.name):
            raise errors.ConflictError(msg='Task Scheduling Already Exist')
        if task_scheduler.type == TaskSchedulerType.CRONTAB:
            crontab_verify(obj.crontab)
        count = await task_scheduler_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def update_status(*, db: AsyncSession, pk: int) -> int:
        """
        Update task scheduling status

        :param db: database session
        :param pk: Task Scheduling ID
        :return:
        """

        task_scheduler = await task_scheduler_dao.get(db, pk)
        if not task_scheduler:
            raise errors.NotFoundError(msg='Task Scheduling does not exist')
        count = await task_scheduler_dao.set_status(db, pk, status=not task_scheduler.enabled)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        Delete task schedule

        :param db: database session
        :param pk: User ID
        :return:
        """

        task_scheduler = await task_scheduler_dao.get(db, pk)
        if not task_scheduler:
            raise errors.NotFoundError(msg='Task Scheduling does not exist')
        count = await task_scheduler_dao.delete(db, pk)
        return count

    @staticmethod
    async def execute(*, db: AsyncSession, pk: int) -> None:
        """
        Perform tasks

        :param db: database session
        :param pk: Task Scheduling ID
        :return:
        """

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
