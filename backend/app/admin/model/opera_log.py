from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class OperaLog(DataClassBase):
    """Operation log table"""

    __tablename__ = 'sys_opera_log'

    id: Mapped[id_key] = mapped_column(init=False)
    trace_id: Mapped[str] = mapped_column(sa.String(32), comment='Request Trace ID')
    username: Mapped[str | None] = mapped_column(sa.String(64), comment='username')
    method: Mapped[str] = mapped_column(sa.String(32), comment='Request method')
    title: Mapped[str] = mapped_column(sa.String(256), comment='Operation module')
    path: Mapped[str] = mapped_column(sa.String(512), comment='Request path')
    ip: Mapped[str] = mapped_column(sa.String(64), comment='IP address')
    country: Mapped[str | None] = mapped_column(sa.String(64), comment='country')
    region: Mapped[str | None] = mapped_column(sa.String(64), comment='region')
    city: Mapped[str | None] = mapped_column(sa.String(64), comment='city')
    user_agent: Mapped[str | None] = mapped_column(sa.String(512), comment='user agent')
    os: Mapped[str | None] = mapped_column(sa.String(64), comment='operating system')
    browser: Mapped[str | None] = mapped_column(sa.String(64), comment='browser')
    device: Mapped[str | None] = mapped_column(sa.String(64), comment='device')
    args: Mapped[str | None] = mapped_column(sa.JSON(), comment='Request Parameters')
    status: Mapped[int] = mapped_column(comment='Operation status (0 abnormal 1 normal)')
    code: Mapped[str] = mapped_column(sa.String(32), insert_default='200', comment='Operation status code')
    msg: Mapped[str | None] = mapped_column(UniversalText, comment='Prompt message')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='Request time (ms)')
    opera_time: Mapped[datetime] = mapped_column(TimeZone, comment='Operation time')
    created_time: Mapped[datetime] = mapped_column(
        TimeZone, init=False, default_factory=timezone.now, comment='Create time'
    )
