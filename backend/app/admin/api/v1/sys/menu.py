#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.admin.schema.menu import CreateMenuParam, GetMenuDetail, UpdateMenuParam
from backend.app.admin.service.menu_service import menu_service
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC

router = APIRouter()


@router.get('/sidebar', summary='get user menu sidebar', description='adapted vben admin v5', dependencies=[DependsJwtAuth])
async def get_user_sidebar(request: Request) -> ResponseSchemaModel[list[dict[str, Any] | None]]:
    menu = await menu_service.get_sidebar(request=request)
    return response_base.success(data=menu)


@router.get('/{pk}', summary='Get menu details', dependencies=[DependsJwtAuth])
async def get_menu(pk: Annotated[int, Path(description='Menu ID')]) -> ResponseSchemaModel[GetMenuDetail]:
    data = await menu_service.get(pk=pk)
    return response_base.success(data=data)


@router.get('', summary='get menu tree', dependencies=[DependsJwtAuth])
async def get_menu_tree(
    title: Annotated[str | None, Query(description='menu title')] = None,
    status: Annotated[int | None, Query(description='Status')] = None,
) -> ResponseSchemaModel[list[dict[str, Any]]]:
    menu = await menu_service.get_tree(title=title, status=status)
    return response_base.success(data=menu)


@router.post(
    '',
    summary='Create menu',
    dependencies=[
        Depends(RequestPermission('sys:menu:add')),
        DependsRBAC,
    ],
)
async def create_menu(obj: CreateMenuParam) -> ResponseModel:
    await menu_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update menu',
    dependencies=[
        Depends(RequestPermission('sys:menu:edit')),
        DependsRBAC,
    ],
)
async def update_menu(pk: Annotated[int, Path(description='Menu ID')], obj: UpdateMenuParam) -> ResponseModel:
    count = await menu_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='Delete menu',
    dependencies=[
        Depends(RequestPermission('sys:menu:del')),
        DependsRBAC,
    ],
)
async def delete_menu(pk: Annotated[int, Path(description='Menu ID')]) -> ResponseModel:
    count = await menu_service.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
