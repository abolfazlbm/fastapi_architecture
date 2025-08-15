#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Request

from backend.app.admin.schema.role import GetRoleDetail
from backend.app.admin.schema.user import (
    AddUserParam,
    GetCurrentUserInfoWithRelationDetail,
    GetUserInfoWithRelationDetail,
    ResetPasswordParam,
    UpdateUserParam,
)
from backend.app.admin.service.user_service import user_service
from backend.common.enums import UserPermissionType
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('/me', summary='Get current user information', dependencies=[DependsJwtAuth])
async def get_current_user(request: Request) -> ResponseSchemaModel[GetCurrentUserInfoWithRelationDetail]:
    data = request.user.model_dump()
    return response_base.success(data=data)


@router.get('/{pk}', summary='Get user information', dependencies=[DependsJwtAuth])
async def get_userinfo(
    pk: Annotated[int, Path(description='User ID')],
) -> ResponseSchemaModel[GetUserInfoWithRelationDetail]:
    data = await user_service.get_userinfo(pk=pk)
    return response_base.success(data=data)


@router.get('/{pk}/roles', summary='Get all roles of users', dependencies=[DependsJwtAuth])
async def get_user_roles(pk: Annotated[int, Path(description='User ID')]) -> ResponseSchemaModel[list[GetRoleDetail]]:
    data = await user_service.get_roles(pk=pk)
    return response_base.success(data=data)


@router.get(
    '',
    summary='Paging to get all users',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_users_paged(
    db: CurrentSession,
    dept: Annotated[int | None, Query(description='Department ID')] = None,
    username: Annotated[str | None, Query(description='Username')] = None,
    phone: Annotated[str | None, Query(description='Phone number')] = None,
    status: Annotated[int | None, Query(description='status')] = None,
) -> ResponseSchemaModel[PageData[GetUserInfoWithRelationDetail]]:
    user_select = await user_service.get_select(dept=dept, username=username, phone=phone, status=status)
    page_data = await paging_data(db, user_select)
    return response_base.success(data=page_data)


@router.post('', summary='Create a user', dependencies=[DependsRBAC])
async def create_user(request: Request, obj: AddUserParam) -> ResponseSchemaModel[GetUserInfoWithRelationDetail]:
    await user_service.create(request=request, obj=obj)
    data = await user_service.get_userinfo(username=obj.username)
    return response_base.success(data=data)


@router.put('/{pk}', summary='Update user information', dependencies=[DependsRBAC])
async def update_user(
    request: Request, pk: Annotated[int, Path(description='User ID')], obj: UpdateUserParam
) -> ResponseModel:
    count = await user_service.update(request=request, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/permissions', summary='Update user permissions', dependencies=[DependsRBAC])
async def update_user_permission(
    request: Request,
    pk: Annotated[int, Path(description='User ID')],
    type: Annotated[UserPermissionType, Query(description='Permission Type')],
) -> ResponseModel:
    count = await user_service.update_permission(request=request, pk=pk, type=type)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/password', summary='Update the current user password', dependencies=[DependsJwtAuth])
async def update_user_password(request: Request, obj: ResetPasswordParam) -> ResponseModel:
    count = await user_service.update_password(request=request, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/password', summary='Reset user password', dependencies=[DependsRBAC])
async def reset_user_password(
    request: Request,
    pk: Annotated[int, Path(description='User ID')],
    password: Annotated[str, Body(embed=True, description='New Password')],
) -> ResponseModel:
    count = await user_service.reset_password(request=request, pk=pk, password=password)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/nickname', summary='Update the current user nickname', dependencies=[DependsJwtAuth])
async def update_user_nickname(
    request: Request, nickname: Annotated[str, Body(embed=True, description='User nickname')]
) -> ResponseModel:
    count = await user_service.update_nickname(request=request, nickname=nickname)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/avatar', summary='Update the current user avatar', dependencies=[DependsJwtAuth])
async def update_user_avatar(
    request: Request, avatar: Annotated[str, Body(embed=True, description='User avatar address')]
) -> ResponseModel:
    count = await user_service.update_avatar(request=request, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/email', summary="Update the current user's email address", dependencies=[DependsJwtAuth])
async def update_user_email(
    request: Request,
    captcha: Annotated[str, Body(embed=True, description='Email verification code')],
    email: Annotated[str, Body(embed=True, description='User email')],
) -> ResponseModel:
    count = await user_service.update_email(request=request, captcha=captcha, email=email)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    path='/{pk}',
    summary='Delete users',
    dependencies=[
        Depends(RequestPermission('sys:user:del')),
        DependsRBAC,
    ],
)
async def delete_user(pk: Annotated[int, Path(description='User ID')]) -> ResponseModel:
    count = await user_service.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
