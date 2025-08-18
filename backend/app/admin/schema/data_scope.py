#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.admin.schema.data_rule import GetDataRuleDetail
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class DataScopeBase(SchemaBase):
    """Data range basic model"""

    name: str = Field(description='name')
    status: StatusType = Field(description='Status')


class CreateDataScopeParam(DataScopeBase):
    """Create data range parameters"""


class UpdateDataScopeParam(DataScopeBase):
    """Update data range parameters"""


class UpdateDataScopeRuleParam(SchemaBase):
    """Update data range rule parameters"""

    rules: list[int] = Field(description='Data rule ID list')


class DeleteDataScopeParam(SchemaBase):
    """Delete data range parameters"""

    pks: list[int] = Field(description='Data range ID list')


class GetDataScopeDetail(DataScopeBase):
    """Data range details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Data range ID')
    created_time: datetime = Field(description='create time')
    updated_time: datetime | None = Field(None, description='Update time')


class GetDataScopeWithRelationDetail(GetDataScopeDetail):
    """Data range association details"""

    rules: list[GetDataRuleDetail] = Field([], description='Data Rule List')
