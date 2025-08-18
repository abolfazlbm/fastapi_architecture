#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import BigInteger, Column, ForeignKey, Table

from backend.common.model import MappedBase

sys_user_role = Table(
    'sys_user_role',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, unique=True, index=True, autoincrement=True, comment='Primary key ID'),
    Column('user_id', BigInteger, ForeignKey('sys_user.id', ondelete='CASCADE'), primary_key=True, comment='User ID'),
    Column('role_id', BigInteger, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True, comment='Role ID'),
)

sys_role_menu = Table(
    'sys_role_menu',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, unique=True, index=True, autoincrement=True, comment='Primary key ID'),
    Column('role_id', BigInteger, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True, comment='Role ID'),
    Column('menu_id', BigInteger, ForeignKey('sys_menu.id', ondelete='CASCADE'), primary_key=True, comment='Menu ID'),
)

sys_role_data_scope = Table(
    'sys_role_data_scope',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, unique=True, index=True, autoincrement=True, comment='Primary key ID'),
    Column('role_id', BigInteger, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True, comment='Role ID'),
    Column(
        'data_scope_id',
        BigInteger,
        ForeignKey('sys_data_scope.id', ondelete='CASCADE'),
        primary_key=True,
        comment='Data scope ID',
    ),
)

sys_data_scope_rule = Table(
    'sys_data_scope_rule',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, unique=True, index=True, autoincrement=True, comment='Primary key ID'),
    Column(
        'data_scope_id',
        BigInteger,
        ForeignKey('sys_data_scope.id', ondelete='CASCADE'),
        primary_key=True,
        comment='Data scope ID',
    ),
    Column(
        'data_rule_id',
        BigInteger,
        ForeignKey('sys_data_rule.id', ondelete='CASCADE'),
        primary_key=True,
        comment='Data Rules ID',
    ),
)
