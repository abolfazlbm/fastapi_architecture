#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from typing import Any

from celery import Task
from sqlalchemy.exc import SQLAlchemyError

from backend.common.socketio.actions import task_notification
from backend.core.conf import settings


class TaskBase(Task):
    """Celery task base class"""

    autoretry_for = (SQLAlchemyError,)
    max_retries = settings.CELERY_TASK_MAX_RETRIES

    async def before_start(self, task_id: str, args, kwargs) -> None:
        """
        Execute the hook before the task begins

        :param task_id: Task ID
        :return:
        """
        await task_notification(msg=f'task {task_id} starts execution')

    async def on_success(self, retval: Any, task_id: str, args, kwargs) -> None:
        """
        Execute the hook after the task is successful

        :param retval: task return value
        :param task_id: Task ID
        :return:
        """
        await task_notification(msg=f'Task {task_id} executed successfully')

    def on_failure(self, exc: Exception, task_id: str, args, kwargs, einfo) -> None:
        """
        Execute hook after task failure

        :param excc: exception object
        :param task_id: Task ID
        :param einfo: Exception information
        :return:
        """
        asyncio.create_task(task_notification(msg=f'task {task_id} failed to execute'))
