#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query

from backend.app.admin.schema.role import (
    CreateRoleParam,
    DeleteRoleParam,
    GetRoleDetail,
    GetRoleWithRelationDetail,
    UpdateRoleMenuParam,
    UpdateRoleParam,
    UpdateRoleScopeParam,
)
from backend.app.admin.service.role_service import role_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('/all', summary='Get all roles', dependencies=[DependsJwtAuth])
async def get_all_roles() -> ResponseSchemaModel[list[GetRoleDetail]]:
    data = await role_service.get_all()
    return response_base.success(data=data)


@router.get('/{pk}/menus', summary='Get the role menu tree', dependencies=[DependsJwtAuth])
async def get_role_menu_tree(
    pk: Annotated[int, Path(description='Role ID')],
) -> ResponseSchemaModel[list[dict[str, Any] | None]]:
    menu = await role_service.get_menu_tree(pk=pk)
    return response_base.success(data=menu)


@router.get('/{pk}/scopes', summary='Get all the data ranges of the role', dependencies=[DependsJwtAuth])
async def get_role_scopes(pk: Annotated[int, Path(description='Role ID')]) -> ResponseSchemaModel[list[int]]:
    rule = await role_service.get_scopes(pk=pk)
    return response_base.success(data=rule)


@router.get('/{pk}', summary='Get character details', dependencies=[DependsJwtAuth])
async def get_role(pk: Annotated[int, Path(description='Role ID')]) -> ResponseSchemaModel[GetRoleWithRelationDetail]:
    data = await role_service.get(pk=pk)
    return response_base.success(data=data)


@router.get(
    '',
    summary='Paging to get all roles',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_roles_paged(
    db: CurrentSession,
    name: Annotated[str | None, Query(description='role name')] = None,
    status: Annotated[int | None, Query(description='status')] = None,
) -> ResponseSchemaModel[PageData[GetRoleDetail]]:
    role_select = await role_service.get_select(name=name, status=status)
    page_data = await paging_data(db, role_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='Create a role',
    dependencies=[
        Depends(RequestPermission('sys:role:add')),
        DependsRBAC,
    ],
)
async def create_role(obj: CreateRoleParam) -> ResponseModel:
    await role_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update roles',
    dependencies=[
        Depends(RequestPermission('sys:role:edit')),
        DependsRBAC,
    ],
)
async def update_role(pk: Annotated[int, Path(description='Role ID')], obj: UpdateRoleParam) -> ResponseModel:
    count = await role_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/menus',
    summary='Update the role menu',
    dependencies=[
        Depends(RequestPermission('sys:role:menu:edit')),
        DependsRBAC,
    ],
)
async def update_role_menus(
    pk: Annotated[int, Path(description='Role ID')], menu_ids: UpdateRoleMenuParam
) -> ResponseModel:
    count = await role_service.update_role_menu(pk=pk, menu_ids=menu_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/scopes',
    summary='Update role data range',
    dependencies=[
        Depends(RequestPermission('sys:role:scope:edit')),
        DependsRBAC,
    ],
)
async def update_role_scopes(
    pk: Annotated[int, Path(description='Role ID')], scope_ids: UpdateRoleScopeParam
) -> ResponseModel:
    count = await role_service.update_role_scope(pk=pk, scope_ids=scope_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='Batch delete roles',
    dependencies=[
        Depends(RequestPermission('sys:role:del')),
        DependsRBAC,
    ],
)
async def delete_roles(obj: DeleteRoleParam) -> ResponseModel:
    count = await role_service.delete(obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
