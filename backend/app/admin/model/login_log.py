from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class LoginLog(DataClassBase):
    """Login log table"""

    __tablename__ = 'sys_login_log'

    id: Mapped[id_key] = mapped_column(init=False)
    user_uuid: Mapped[str] = mapped_column(sa.String(64), comment='User UUID')
    username: Mapped[str] = mapped_column(sa.String(64), comment='Username')
    status: Mapped[int] = mapped_column(insert_default=0, comment='Login status (0 failed 1 successful)')
    ip: Mapped[str] = mapped_column(sa.String(64), comment='Login IP address')
    country: Mapped[str | None] = mapped_column(sa.String(64), comment='Country')
    region: Mapped[str | None] = mapped_column(sa.String(64), comment='region')
    city: Mapped[str | None] = mapped_column(sa.String(64), comment='City')
    user_agent: Mapped[str] = mapped_column(sa.String(256), comment='request header')
    os: Mapped[str | None] = mapped_column(sa.String(64), comment='OS')
    browser: Mapped[str | None] = mapped_column(sa.String(64), comment='browser')
    device: Mapped[str | None] = mapped_column(sa.String(64), comment='device')
    msg: Mapped[str] = mapped_column(UniversalText, comment='prompt message')
    login_time: Mapped[datetime] = mapped_column(TimeZone, comment='Login time')
    created_time: Mapped[datetime] = mapped_column(
        TimeZone,
        init=False,
        default_factory=timezone.now,
        comment='Create time',
    )
