import asyncio

from datetime import datetime
from typing import ClassVar

import sqlalchemy as sa

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enums import StatusType
from backend.common.exception import errors
from backend.common.model import Base, TimeZone, UniversalText, id_key
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.timezone import timezone


class TaskScheduler(Base):
    """Task schedule"""

    __tablename__ = 'task_scheduler'
    __table_args__ = (
        sa.UniqueConstraint('name', 'deleted', name='uk_task_scheduler_name_deleted'),
        {'comment': 'Task schedule'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), comment='Task name')
    task: Mapped[str] = mapped_column(sa.String(256), comment='Celery task to run')
    args: Mapped[str | None] = mapped_column(sa.JSON(), comment='Positional arguments accepted by the task')
    kwargs: Mapped[str | None] = mapped_column(sa.JSON(), comment='Keyword arguments accepted by the task')
    queue: Mapped[str | None] = mapped_column(sa.String(256), comment='Queue defined in CELERY_TASK_QUEUES')
    exchange: Mapped[str | None] = mapped_column(sa.String(256), comment='Exchange for low-level AMQP routing')
    routing_key: Mapped[str | None] = mapped_column(sa.String(256), comment='Routing key for low-level AMQP routing')
    start_time: Mapped[datetime | None] = mapped_column(TimeZone, comment='Time when the task starts being triggered')
    expire_time: Mapped[datetime | None] = mapped_column(TimeZone, comment='Deadline for task execution')
    expire_seconds: Mapped[int | None] = mapped_column(comment='Task expiration offset in seconds')
    type: Mapped[int] = mapped_column(comment='Schedule type (0: interval, 1: crontab)')
    interval_every: Mapped[int | None] = mapped_column(comment='Number of intervals before the task runs again')
    interval_period: Mapped[str | None] = mapped_column(sa.String(256), comment='Interval unit between task runs')
    crontab: Mapped[str | None] = mapped_column(sa.String(64), default='* * * * *', comment='Crontab expression')
    one_off: Mapped[bool] = mapped_column(default=False, comment='Whether to run only once')
    status: Mapped[int] = mapped_column(default=StatusType.enable.value, comment='Status (0: disabled, 1: enabled)')
    total_run_count: Mapped[int] = mapped_column(default=0, comment='Total number of task triggers')
    last_run_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='Last task trigger time')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remarks')

    no_changes: bool = False
    # Keep references to background tasks so tasks returned by create_task are not collected before execution
    _update_tasks: ClassVar[set[asyncio.Task]] = set()

    @staticmethod
    def before_insert_or_update(mapper, connection, target) -> None:  # ruff:ignore[missing-type-function-argument]
        if target.expire_seconds is not None and target.expire_time:
            raise errors.ConflictError(msg='expires and expire_seconds can only be set to one')

    @classmethod
    def changed(cls, mapper, connection, target) -> None:  # ruff:ignore[missing-type-function-argument]
        if not target.no_changes:
            cls.update_changed(mapper, connection, target)

    @classmethod
    async def update_changed_async(cls) -> None:
        now = timezone.now()
        await redis_client.set(f'{settings.CELERY_REDIS_PREFIX}:last_update', timezone.to_str(now))

    @classmethod
    def update_changed(cls, mapper, connection, target) -> None:  # ruff:ignore[missing-type-function-argument]
        task = asyncio.create_task(cls.update_changed_async())
        cls._update_tasks.add(task)
        task.add_done_callback(cls._update_tasks.discard)


# Event listener
event.listen(TaskScheduler, 'before_insert', TaskScheduler.before_insert_or_update)
event.listen(TaskScheduler, 'before_update', TaskScheduler.before_insert_or_update)
event.listen(TaskScheduler, 'after_insert', TaskScheduler.update_changed)
event.listen(TaskScheduler, 'after_delete', TaskScheduler.update_changed)
event.listen(TaskScheduler, 'after_update', TaskScheduler.changed)
