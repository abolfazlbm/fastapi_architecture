#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import CustomEmailStr, CustomPhoneNumber, SchemaBase


class DeptSchemaBase(SchemaBase):
    """Departmental Basic Model"""

    name: str = Field(description='department name')
    parent_id: int | None = Field(None, description='Department Parent ID')
    sort: int = Field(0, ge=0, description='Sort')
    leader: str | None = Field(None, description='Person in charge')
    phone: CustomPhoneNumber | None = Field(None, description='Contact Number')
    email: CustomEmailStr | None = Field(None, description='Email')
    status: StatusType = Field(description='Status')


class CreateDeptParam(DeptSchemaBase):
    """Create department parameters"""


class UpdateDeptParam(DeptSchemaBase):
    """Update department parameters"""


class GetDeptDetail(DeptSchemaBase):
    """Department details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Department ID')
    del_flag: bool = Field(description='Whether to delete')
    created_time: datetime = Field(description='create time')
    updated_time: datetime | None = Field(None, description='Update time')