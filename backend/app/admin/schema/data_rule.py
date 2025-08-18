#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import RoleDataRuleExpressionType, RoleDataRuleOperatorType
from backend.common.schema import SchemaBase


class DataRuleSchemaBase(SchemaBase):
    """Basic Model of Data Rules"""

    name: str = Field(description='rule name')
    model: str = Field(description='model name')
    column: str = Field(description='field name')
    operator: RoleDataRuleOperatorType = Field(description='operator (AND/OR)')
    expression: RoleDataRuleExpressionType = Field(description='Expression type')
    value: str = Field(description='rule value')

class CreateDataRuleParam(DataRuleSchemaBase):
    """Create data rule parameters"""


class UpdateDataRuleParam(DataRuleSchemaBase):
    """Update data rule parameters"""


class DeleteDataRuleParam(SchemaBase):
    """Delete data rule parameters"""

    pks: list[int] = Field(description='Rule ID List')


class GetDataRuleDetail(DataRuleSchemaBase):
    """Data Rule Details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Rule ID')
    created_time: datetime = Field(description='create time')
    updated_time: datetime | None = Field(None, description='Update time')


class GetDataRuleColumnDetail(SchemaBase):
    """Data rules available model fields details"""

    key: str = Field(description='field name')
    comment: str = Field(description='field comment')
