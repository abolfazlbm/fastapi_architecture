#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import Field

from backend.app.admin.schema.user import GetUserInfoDetail
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class GetSwaggerToken(SchemaBase):
    """Swagger authentication token"""

    access_token: str = Field(description='Access Token')
    token_type: str = Field('Bearer', description='Token type')
    user: GetUserInfoDetail = Field(description='User Information')


class AccessTokenBase(SchemaBase):
    """Access token basic model"""

    access_token: str = Field(description='Access Token')
    access_token_expire_time: datetime = Field(description='token expiration time')
    session_uuid: str = Field(description='session UUID')


class GetNewToken(AccessTokenBase):
    """Get new token"""


class GetLoginToken(AccessTokenBase):
    """Get login token"""

    user: GetUserInfoDetail = Field(description='User Information')


class GetTokenDetail(SchemaBase):
    """Token details"""

    id: int = Field(description='User ID')
    session_uuid: str = Field(description='session UUID')
    username: str = Field(description='Username')
    nickname: str = Field(description='nickname')
    ip: str = Field(description='IP address')
    os: str = Field(description='OS')
    browser: str = Field(description='browser')
    device: str = Field(description='device')
    status: StatusType = Field(description='Status')
    last_login_time: str = Field(description='Last login time')
    expire_time: datetime = Field(description='Expiration time')
