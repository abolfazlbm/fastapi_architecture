#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.admin.model.m2m import sys_role_menu
from backend.common.model import Base, id_key

if TYPE_CHECKING:
    from backend.app.admin.model import Role


class Menu(Base):
    """Menu Table"""

    __tablename__ = 'sys_menu'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(String(50), comment='menu title')
    name: Mapped[str] = mapped_column(String(50), comment='menu name')
    path: Mapped[str | None] = mapped_column(String(200), comment='Route Address')
    sort: Mapped[int] = mapped_column(default=0, comment='Sort')
    icon: Mapped[str | None] = mapped_column(String(100), default=None, comment='menu icon')
    type: Mapped[int] = mapped_column(default=0, comment='Menu type (0 directory 1 menu 2 buttons 3 embedded 4 external links)')
    component: Mapped[str | None] = mapped_column(String(255), default=None, comment='Component Path')
    perms: Mapped[str | None] = mapped_column(String(100), default=None, comment='Permission Identification')
    status: Mapped[int] = mapped_column(default=1, comment='menu status (0 is disabled 1 is normal)')
    display: Mapped[int] = mapped_column(default=1, comment='whether it is displayed (0 no 1 yes)')
    cache: Mapped[int] = mapped_column(default=1, comment='Whether to cache (0 No 1 Yes)')
    link: Mapped[str | None] = mapped_column(
        LONGTEXT().with_variant(TEXT, 'postgresql'), default=None, comment='External link address'
    )
    remark: Mapped[str | None] = mapped_column(
        LONGTEXT().with_variant(TEXT, 'postgresql'), default=None, comment='Remarks'
    )

    # Parent menu one-to-many
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey('sys_menu.id', ondelete='SET NULL'), default=None, index=True, comment='Parent menu ID'
    )
    parent: Mapped[Optional['Menu']] = relationship(init=False, back_populates='children', remote_side=[id])
    children: Mapped[Optional[list['Menu']]] = relationship(init=False, back_populates='parent')

    # Menu roles many to many
    roles: Mapped[list[Role]] = relationship(init=False, secondary=sys_role_menu, back_populates='menus')
