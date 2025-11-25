from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class OperaLog(DataClassBase):
    """Operation log table"""

    __tablename__ = 'sys_opera_log'

    id: Mapped[id_key] = mapped_column(init=False)
    trace_id: Mapped[str] = mapped_column(sa.String(32), comment='Request Tracking ID')
    username: Mapped[str | None] = mapped_column(sa.String(64), comment='Username')
    method: Mapped[str] = mapped_column(sa.String(32), comment='Request Type')
    title: Mapped[str] = mapped_column(sa.String(256), comment='Operation module')
    path: Mapped[str] = mapped_column(sa.String(512), comment='Request path')
    ip: Mapped[str] = mapped_column(sa.String(64), comment='IP address')
    country: Mapped[str | None] = mapped_column(sa.String(64), comment='Country')
    region: Mapped[str | None] = mapped_column(sa.String(64), comment='region')
    city: Mapped[str | None] = mapped_column(sa.String(64), comment='City')
    user_agent: Mapped[str] = mapped_column(sa.String(512), comment='request header')
    os: Mapped[str | None] = mapped_column(sa.String(64), comment='OS')
    browser: Mapped[str | None] = mapped_column(sa.String(64), comment='browser')
    device: Mapped[str | None] = mapped_column(sa.String(64), comment='device')
    args: Mapped[str | None] = mapped_column(sa.JSON(), comment='request parameter')
    status: Mapped[int] = mapped_column(comment='Operation status (0 exception 1 normal)')
    code: Mapped[str] = mapped_column(sa.String(32), insert_default='200', comment='Operation status code')
    msg: Mapped[str | None] = mapped_column(UniversalText, comment='prompt message')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='Request time taken (ms)')
    opera_time: Mapped[datetime] = mapped_column(TimeZone, comment='operation time')
    created_time: Mapped[datetime] = mapped_column(
        TimeZone, init=False, default_factory=timezone.now, comment='Create time'
    )
