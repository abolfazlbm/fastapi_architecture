#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field
from pydantic.types import JsonValue

from backend.app.task.enums import PeriodType, TaskSchedulerType
from backend.common.schema import SchemaBase


class TaskSchedulerSchemeBase(SchemaBase):
    """Task scheduling parameters"""

    name: str = Field(description='Task name')
    task: str = Field(description='The Celery task to run')
    args: JsonValue | None = Field(default=None, description='Position parameters that can be received by the task')
    kwargs: JsonValue | None = Field(default=None, description='Keyword parameters that the task can receive')
    queue: str | None = Field(default=None, description='CELERY_TASK_QUEUES queue defined in ')
    exchange: str | None = Field(default=None, description='Switches with low-level AMQP routes')
    routing_key: str | None = Field(default=None, description='The routing key for low-level AMQP routes')
    start_time: datetime | None = Field(default=None, description='The time when the task starts to trigger')
    expire_time: datetime | None = Field(default=None, description='The deadline at which the task is no longer triggered')
    expire_seconds: int | None = Field(default=None, description='The time difference between the seconds when the task is no longer triggered')
    type: TaskSchedulerType = Field(description='Task scheduling type (0 interval, 1 timing)')
    interval_every: int | None = Field(default=None, description='The number of intervals before the task runs again')
    interval_period: PeriodType | None = Field(default=None, description='The type of cycle between task runs')
    crontab: str = Field(default='* * * * *', description='Run the Crontab expression')
    one_off: bool = Field(default=False, description='Whether it is run only once')
    remark: str | None = Field(default=None, description='Remark')


class CreateTaskSchedulerParam(TaskSchedulerSchemeBase):
    """Create task scheduling parameters"""


class UpdateTaskSchedulerParam(TaskSchedulerSchemeBase):
    """Update task scheduling parameters"""


class GetTaskSchedulerDetail(TaskSchedulerSchemeBase):
    """Task scheduling details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Task scheduling ID')
    enabled: bool = Field(description='Whether the task is enabled')
    total_run_count: int = Field(description='Total number of runs')
    last_run_time: datetime | None = Field(None, description='Last run time')
    created_time: datetime = Field(description='Creation time')
    updated_time: datetime | None = Field(None, description='Update time')
