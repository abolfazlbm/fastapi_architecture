#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.admin.model.m2m import sys_data_scope_rule
from backend.common.model import Base, id_key

if TYPE_CHECKING:
    from backend.app.admin.model import DataScope


class DataRule(Base):
    """Data Rule Table"""

    __tablename__ = 'sys_data_rule'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(500), unique=True, comment='Name')
    model: Mapped[str] = mapped_column(String(50), comment='SQL model name, corresponding to DATA_PERMISSION_MODELS key name')
    column: Mapped[str] = mapped_column(String(20), comment='Model field name')
    operator: Mapped[int] = mapped_column(comment='operator (0:and, 1:or)')
    expression: Mapped[int] = mapped_column(
        comment='Expression (0:==, 1:!=, 2:>, 3:>=, 4:<, 5:<=, 6: in, 7: not_in)'
    )
    value: Mapped[str] = mapped_column(String(255), comment='rule value')

    # Data range rules many to many
    scopes: Mapped[list[DataScope]] = relationship(init=False, secondary=sys_data_scope_rule, back_populates='rules')
