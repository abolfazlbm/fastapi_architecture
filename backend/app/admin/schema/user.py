#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field, HttpUrl, model_validator
from typing_extensions import Self

from backend.app.admin.schema.dept import GetDeptDetail
from backend.app.admin.schema.role import GetRoleWithRelationDetail
from backend.common.enums import StatusType
from backend.common.schema import CustomEmailStr, CustomPhoneNumber, SchemaBase


class AuthSchemaBase(SchemaBase):
    """Basic Model of User Authentication"""

    username: str = Field(description='Username')
    password: str = Field(description='password')


class AuthLoginParam(AuthSchemaBase):
    """User Login Parameters"""

    captcha: str = Field(description='verification code')


class AddUserParam(AuthSchemaBase):
    """Add user parameters"""

    nickname: str | None = Field(None, description='Nickname')
    email: CustomEmailStr | None = Field(None, description='Email')
    phone: CustomPhoneNumber | None = Field(None, description='Mobile Number')
    dept_id: int = Field(description='Department ID')
    roles: list[int] = Field(description='Role ID List')

class AddOAuth2UserParam(AuthSchemaBase):
    """Add OAuth2 user parameters"""

    password: str | None = Field(None, description='password')
    nickname: str | None = Field(None, description='Nickname')
    email: CustomEmailStr | None = Field(None, description='Email')
    avatar: HttpUrl | None = Field(None, description='Avatar address')


class ResetPasswordParam(SchemaBase):
    """Reset password parameters"""

    old_password: str = Field(description='old password')
    new_password: str = Field(description='new password')
    confirm_password: str = Field(description='Confirm Password')


class UserInfoSchemaBase(SchemaBase):
    """Basic Model of User Information"""

    dept_id: int | None = Field(None, description='Department ID')
    username: str = Field(description='Username')
    nickname: str = Field(description='nickname')
    avatar: HttpUrl | None = Field(None, description='Avatar address')
    email: CustomEmailStr | None = Field(None, description='Email')
    phone: CustomPhoneNumber | None = Field(None, description='Phone Number')

class UpdateUserParam(UserInfoSchemaBase):
    """Update user parameters"""

    roles: list[int] = Field(description='Role ID List')


class GetUserInfoDetail(UserInfoSchemaBase):
    """User Information Details"""

    model_config = ConfigDict(from_attributes=True)

    dept_id: int | None = Field(None, description='Department ID')
    id: int = Field(description='User ID')
    uuid: str = Field(description='User UUID')
    status: StatusType = Field(description='Status')
    is_superuser: bool = Field(description='Is it super administrator')
    is_staff: bool = Field(description='Administrator')
    is_multi_login: bool = Field(description='Whether multi-end login is allowed')
    join_time: datetime = Field(description='joining time')
    last_login_time: datetime | None = Field(None, description='Last login time')


class GetUserInfoWithRelationDetail(GetUserInfoDetail):
    """User Information Related Details"""

    model_config = ConfigDict(from_attributes=True)

    dept: GetDeptDetail | None = Field(None, description='Department Information')
    roles: list[GetRoleWithRelationDetail] = Field(description='Role list')


class GetCurrentUserInfoWithRelationDetail(GetUserInfoWithRelationDetail):
    """Current user information association details"""

    model_config = ConfigDict(from_attributes=True)

    dept: str | None = Field(None, description='Department Name')
    roles: list[str] = Field(description='Role Name List')

    @model_validator(mode='before')
    @classmethod
    def handel(cls, data: Any) -> Self:
        """Processing department and role data"""
        dept = data['dept']
        if dept:
            data['dept'] = dept['name']
        roles = data['roles']
        if roles:
            data['roles'] = [role['name'] for role in roles]
        return data
