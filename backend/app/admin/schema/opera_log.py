#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class OperaLogSchemaBase(SchemaBase):
    """Basic Model of Operation Log"""

    trace_id: str = Field(description='tracking ID')
    username: str | None = Field(None, description='Username')
    method: str = Field(description='request method')
    title: str = Field(description='Operation title')
    path: str = Field(description='request path')
    ip: str = Field(description='IP address')
    country: str | None = Field(None, description='Country')
    region: str | None = Field(None, description='region')
    city: str | None = Field(None, description='City')
    user_agent: str = Field(description='user agent')
    os: str | None = Field(None, description='OS')
    browser: str | None = Field(None, description='browser')
    device: str | None = Field(None, description='device')
    args: dict[str, Any] | None = Field(None, description='Request Parameter')
    status: StatusType = Field(description='Status')
    code: str = Field(description='status code')
    msg: str | None = Field(None, description='Message')
    cost_time: float = Field(description='time-consuming')
    opera_time: datetime = Field(description='operation time')


class CreateOperaLogParam(OperaLogSchemaBase):
    """Create operation log parameters"""


class UpdateOperaLogParam(OperaLogSchemaBase):
    """Update operation log parameters"""


class DeleteOperaLogParam(SchemaBase):
    """Delete operation log parameters"""

    pks: list[int] = Field(description='Operation log ID list')


class GetOperaLogDetail(OperaLogSchemaBase):
    """Operation log details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='log ID')
    created_time: datetime = Field(description='create time')
