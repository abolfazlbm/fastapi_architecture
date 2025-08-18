#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class LoginLogSchemaBase(SchemaBase):
    """Login log basic model"""

    user_uuid: str = Field(description='User UUID')
    username: str = Field(description='Username')
    status: int = Field(description='Login status')
    ip: str = Field(description='IP address')
    country: str | None = Field(None, description='Country')
    region: str | None = Field(None, description='region')
    city: str | None = Field(None, description='City')
    user_agent: str = Field(description='User agent')
    browser: str | None = Field(None, description='Browser')
    os: str | None = Field(None, description='OS')
    device: str | None = Field(None, description='Device')
    msg: str = Field(description='Message')
    login_time: datetime = Field(description='Login time')


class CreateLoginLogParam(LoginLogSchemaBase):
    """Create login parameters"""


class UpdateLoginLogParam(LoginLogSchemaBase):
    """Update log parameters"""


class DeleteLoginLogParam(SchemaBase):
    """Delete login log parameters"""

    pks: list[int] = Field(description='Login log ID list')


class GetLoginLogDetail(LoginLogSchemaBase):
    """Login log details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='log ID')
    created_time: datetime = Field(description='create time')
