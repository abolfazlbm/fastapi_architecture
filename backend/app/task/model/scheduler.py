import asyncio

from datetime import datetime

import sqlalchemy as sa

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column

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
    name: Mapped[str] = mapped_column(sa.String(64), comment='task name')
    task: Mapped[str] = mapped_column(sa.String(256), comment='Celery task to run')
    args: Mapped[str | None] = mapped_column(sa.JSON(), comment='Positional parameters that the task can receive')
    kwargs: Mapped[str | None] = mapped_column(sa.JSON(), comment='Keyword parameters that the task can receive')
    queue: Mapped[str | None] = mapped_column(sa.String(256), comment='Queue defined in CELERY_TASK_QUEUES')
    exchange: Mapped[str | None] = mapped_column(sa.String(256), comment='Exchange for low-level AMQP routing')
    routing_key: Mapped[str | None] = mapped_column(sa.String(256), comment='Routing key for low-level AMQP routing')
    start_time: Mapped[datetime | None] = mapped_column(TimeZone, comment='The time when the task started to be triggered')
    expire_time: Mapped[datetime | None] = mapped_column(TimeZone, comment='Deadline time when the task is no longer triggered')
    expire_seconds: Mapped[int | None] = mapped_column(comment='The number of seconds the task will no longer trigger')
    type: Mapped[int] = mapped_column(comment='Scheduling type (0 interval 1 timing)')
    interval_every: Mapped[int | None] = mapped_column(comment='Number of intervals before the task runs again')
    interval_period: Mapped[str | None] = mapped_column(sa.String(256), comment='Period type between task runs')
    crontab: Mapped[str | None] = mapped_column(sa.String(64), default='* * * * *', comment='Crontab expression')
    one_off: Mapped[bool] = mapped_column(default=False, comment='Whether to run only once')
    enabled: Mapped[bool] = mapped_column(default=True, comment='Whether to enable the task')
    total_run_count: Mapped[int] = mapped_column(default=0, comment='Total number of task triggers')
    last_run_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='The last time the task was triggered')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remark')

    no_changes: bool = False

    @staticmethod
    def before_insert_or_update(mapper, connection, target) -> None:  # noqa: ANN001
        if target.expire_seconds is not None and target.expire_time:
            raise errors.ConflictError(msg='expires and expire_seconds can only be set to one')

    @classmethod
    def changed(cls, mapper, connection, target) -> None:  # noqa: ANN001
        if not target.no_changes:
            cls.update_changed(mapper, connection, target)

    @classmethod
    async def update_changed_async(cls) -> None:
        now = timezone.now()
        await redis_client.set(f'{settings.CELERY_REDIS_PREFIX}:last_update', timezone.to_str(now))

    @classmethod
    def update_changed(cls, mapper, connection, target) -> None:  # noqa: ANN001
        asyncio.create_task(cls.update_changed_async())


# Event listener
event.listen(TaskScheduler, 'before_insert', TaskScheduler.before_insert_or_update)
event.listen(TaskScheduler, 'before_update', TaskScheduler.before_insert_or_update)
event.listen(TaskScheduler, 'after_insert', TaskScheduler.update_changed)
event.listen(TaskScheduler, 'after_delete', TaskScheduler.update_changed)
event.listen(TaskScheduler, 'after_update', TaskScheduler.changed)
