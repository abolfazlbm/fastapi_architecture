#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field, field_serializer

from backend.app.task import celery_app
from backend.common.schema import SchemaBase


class TaskResultSchemaBase(SchemaBase):
    """Task Outcome Foundation Model"""

    task_id: str = Field(description='Task ID')
    status: str = Field(description='Execution status')
    result: Any | None = Field(description='Execution results')
    date_done: datetime | None = Field(description='End time')
    traceback: str | None = Field(description='Error backlidding')
    name: str | None = Field(description='Task name')
    args: bytes | None = Field(description='Task position parameters')
    kwargs: bytes | None = Field(description='Task keyword parameters')
    worker: str | None = Field(description='Run the Worker')
    retries: int | None = Field(description='Number of reattempts')
    queue: str | None = Field(description='Run queues')


class DeleteTaskResultParam(SchemaBase):
    """Delete the task result parameter"""

    pks: list[int] = Field(description='List of task result IDs')


class GetTaskResultDetail(TaskResultSchemaBase):
    """Details of the task result"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Mission results ID')

    @field_serializer('args', 'kwargs', when_used='unless-none')
    def serialize_params(self, value: bytes | None, _info) -> Any:
        return celery_app.backend.decode(value)
