from datetime import datetime

from pydantic import ConfigDict, Field
from pydantic.types import JsonValue

from backend.app.task.enums import PeriodType, TaskSchedulerType
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class TaskSchedulerSchemaBase(SchemaBase):
    """Task scheduling parameters"""

    name: str = Field(description='task name')
    task: str = Field(description='Celery task to run')
    args: JsonValue | None = Field(None, description='Positional parameters that the task can receive')
    kwargs: JsonValue | None = Field(None, description='Keyword parameters that the task can receive')
    queue: str | None = Field(None, description='Queue defined in CELERY_TASK_QUEUES')
    exchange: str | None = Field(None, description='Switch for low-level AMQP routing')
    routing_key: str | None = Field(None, description='Routing key for low-level AMQP routing')
    start_time: datetime | None = Field(None, description='The time when the task starts to be triggered')
    expire_time: datetime | None = Field(None, description='Deadline time when the task is no longer triggered')
    expire_seconds: int | None = Field(None, description='The number of seconds the task will no longer trigger')
    type: TaskSchedulerType = Field(description='Task scheduling type (0 interval 1 timing)')
    interval_every: int | None = Field(None, description='Number of intervals before the task runs again')
    interval_period: PeriodType | None = Field(None, description='Period type between task runs')
    crontab: str = Field(default='* * * * *', description='Crontab expression')
    one_off: bool = Field(default=False, description='Whether to run only once')
    remark: str | None = Field(None, description='Remarks')


class CreateTaskSchedulerParam(TaskSchedulerSchemaBase):
    """Create task scheduling parameters"""


class UpdateTaskSchedulerParam(TaskSchedulerSchemaBase):
    """Update task scheduling parameters"""


class GetTaskSchedulerDetail(TaskSchedulerSchemaBase):
    """Task scheduling details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='任务调度 ID')
    status: StatusType = Field(description='状态')
    total_run_count: int = Field(description='已运行总次数')
    last_run_time: datetime | None = Field(None, description='最后运行时间')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
