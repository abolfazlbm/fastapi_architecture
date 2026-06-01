from datetime import datetime

from pydantic import ConfigDict, Field
from pydantic.types import JsonValue

from backend.app.task.enums import PeriodType, TaskSchedulerType
from backend.common.schema import SchemaBase


class TaskSchedulerSchemeBase(SchemaBase):
    """Task scheduling parameters"""

    name: str = Field(description='task name')
    task: str = Field(description='Celery task to run')
    args: JsonValue | None = Field(default=None, description='Positional parameters that the task can receive')
    kwargs: JsonValue | None = Field(default=None, description='Keyword parameters that the task can receive')
    queue: str | None = Field(default=None, description='Queue defined in CELERY_TASK_QUEUES')
    exchange: str | None = Field(default=None, description='Switch for low-level AMQP routing')
    routing_key: str | None = Field(default=None, description='Routing key for low-level AMQP routing')
    start_time: datetime | None = Field(default=None, description='The time when the task starts to be triggered')
    expire_time: datetime | None = Field(default=None, description='Deadline time when the task is no longer triggered')
    expire_seconds: int | None = Field(default=None, description='The number of seconds the task will no longer trigger')
    type: TaskSchedulerType = Field(description='Task scheduling type (0 interval 1 timing)')
    interval_every: int | None = Field(default=None, description='Number of intervals before the task runs again')
    interval_period: PeriodType | None = Field(default=None, description='Period type between task runs')
    crontab: str = Field(default='* * * * *', description='Crontab expression')
    one_off: bool = Field(default=False, description='Whether to run only once')
    remark: str | None = Field(default=None, description='Remarks')


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
