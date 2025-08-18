#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import VARBINARY, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import BYTEA, INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.admin.model.m2m import sys_user_role
from backend.common.model import Base, id_key
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from backend.app.admin.model import Dept, Role


class User(Base):
    """User table"""

    __tablename__ = 'sys_user'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='Username')
    nickname: Mapped[str] = mapped_column(String(20), comment='Nickname')
    password: Mapped[str | None] = mapped_column(String(255), comment='password')
    salt: Mapped[bytes | None] = mapped_column(VARBINARY(255).with_variant(BYTEA(255), 'postgresql'), comment='encrypted salt')
    email: Mapped[str | None] = mapped_column(String(50), default=None, unique=True, index=True, comment='email')
    phone: Mapped[str | None] = mapped_column(String(11), default=None, comment='Phone Number')
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment='Avatar')
    status: Mapped[int] = mapped_column(default=1, index=True, comment='User account status (0 is disabled, 1 is normal)')
    is_superuser: Mapped[bool] = mapped_column(
        Boolean().with_variant(INTEGER, 'postgresql'), default=False, comment='Super permission (0 No 1 Yes)'
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean().with_variant(INTEGER, 'postgresql'), default=False, comment='Backend management login (0 No 1 Yes)'
    )
    is_multi_login: Mapped[bool] = mapped_column(
        Boolean().with_variant(INTEGER, 'postgresql'), default=False, comment='Whether to log in repeatedly (0 No 1 Yes)'
    )
    join_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='Register time'
    )
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, onupdate=timezone.now, comment='Last login'
    )

    # One-to-many department users
    dept_id: Mapped[int | None] = mapped_column(
        ForeignKey('sys_dept.id', ondelete='SET NULL'), default=None, comment='Department Association ID'
    )
    dept: Mapped[Dept | None] = relationship(init=False, back_populates='users')

    # Many-to-many user roles
    roles: Mapped[list[Role]] = relationship(init=False, secondary=sys_user_role, back_populates='users')
