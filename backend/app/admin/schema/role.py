#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.admin.schema.data_scope import GetDataScopeDetail
from backend.app.admin.schema.menu import GetMenuDetail
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class RoleSchemaBase(SchemaBase):
    """Role Basic Model"""

    name: str = Field(description='Role name')
    status: StatusType = Field(description='Status')
    is_filter_scopes: bool = Field(True, description='Filter data permission')
    remark: str | None = Field(None, description='Remark')


class CreateRoleParam(RoleSchemaBase):
    """Create role parameters"""


class UpdateRoleParam(RoleSchemaBase):
    """Update role parameters"""


class DeleteRoleParam(SchemaBase):
    """Delete role parameters"""

    pks: list[int] = Field(description='role ID list')


class UpdateRoleMenuParam(SchemaBase):
    """Update role menu parameters"""

    menus: list[int] = Field(description='menu ID list')


class UpdateRoleScopeParam(SchemaBase):
    """Update role data range parameters"""

    scopes: list[int] = Field(description='Data range ID list')


class GetRoleDetail(RoleSchemaBase):
    """Role details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='role ID')
    created_time: datetime = Field(description='create time')
    updated_time: datetime | None = Field(None, description='Update time')


class GetRoleWithRelationDetail(GetRoleDetail):
    """Role Relationship Details"""

    menus: list[GetMenuDetail | None] = Field([], description='Men Detail List')
    scopes: list[GetDataScopeDetail | None] = Field([], description='Data range list')