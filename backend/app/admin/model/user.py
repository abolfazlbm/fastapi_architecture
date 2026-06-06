from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, id_key
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class User(Base):
    """User table"""

    __tablename__ = 'sys_user'
    __table_args__ = (
        sa.UniqueConstraint('username', 'deleted', name='uk_sys_user_username_deleted'),
        sa.UniqueConstraint('email', 'deleted', name='uk_sys_user_email_deleted'),
        {'comment': 'User table'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(sa.String(64), init=False, default_factory=uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, comment='Username')
    nickname: Mapped[str] = mapped_column(sa.String(64), comment='Nickname')
    password: Mapped[str | None] = mapped_column(sa.String(256), comment='Password')
    salt: Mapped[bytes | None] = mapped_column(sa.LargeBinary(256), comment='Encrypted salt')
    email: Mapped[str | None] = mapped_column(sa.String(256), default=None, index=True, comment='Email')
    phone: Mapped[str | None] = mapped_column(sa.String(11), default=None, comment='Phone Number')
    avatar: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='Avatar')
    status: Mapped[int] = mapped_column(default=1, index=True, comment='User account status (0 is disabled, 1 is normal)')
    is_superuser: Mapped[bool] = mapped_column(default=False, comment='Super permission (0 No 1 Yes)')
    is_staff: Mapped[bool] = mapped_column(default=False, comment='Backend management login (0 No 1 Yes)')
    is_multi_login: Mapped[bool] = mapped_column(default=False, comment='Whether to log in repeatedly (0 No 1 Yes)')
    join_time: Mapped[datetime] = mapped_column(TimeZone, init=False, default_factory=timezone.now, comment='Register time')
    last_login_time: Mapped[datetime | None] = mapped_column(
        TimeZone, init=False, onupdate=timezone.now, comment='Last login time'
    )
    last_password_changed_time: Mapped[datetime | None] = mapped_column(
        TimeZone, init=False, default_factory=timezone.now, comment='Last password change time'
    )

    # logical foreign key
    dept_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='Department association ID')
