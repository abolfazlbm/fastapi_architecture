#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.admin.schema.data_scope import (
    CreateDataScopeParam,
    DeleteDataScopeParam,
    GetDataScopeDetail,
    GetDataScopeWithRelationDetail,
    UpdateDataScopeParam,
    UpdateDataScopeRuleParam,
)
from backend.app.admin.service.data_scope_service import data_scope_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('/all', summary='Get all data scopes', dependencies=[DependsJwtAuth])
async def get_all_data_scope() -> ResponseSchemaModel[list[GetDataScopeDetail]]:
    data = await data_scope_service.get_all()
    return response_base.success(data=data)


@router.get('/{pk}', summary='Get data scope details', dependencies=[DependsJwtAuth])
async def get_data_scope(
    pk: Annotated[int, Path(description='Data scope ID')],
) -> ResponseSchemaModel[GetDataScopeDetail]:
    data = await data_scope_service.get(pk=pk)
    return response_base.success(data=data)


@router.get('/{pk}/rules', summary='Get all rules for data scope', dependencies=[DependsJwtAuth])
async def get_data_scope_rules(
    pk: Annotated[int, Path(description='Data scope ID')],
) -> ResponseSchemaModel[GetDataScopeWithRelationDetail]:
    data = await data_scope_service.get_rules(pk=pk)
    return response_base.success(data=data)


@router.get(
    '',
    summary='Paging to get all data scopes',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_data_scopes_paged(
    db: CurrentSession,
    name: Annotated[str | None, Query(description='Scope name')] = None,
    status: Annotated[int | None, Query(description='Status')] = None,
) -> ResponseSchemaModel[PageData[GetDataScopeDetail]]:
    data_scope_select = await data_scope_service.get_select(name=name, status=status)
    page_data = await paging_data(db, data_scope_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='Create data scope',
    dependencies=[
        Depends(RequestPermission('data:scope:add')),
        DependsRBAC,
    ],
)
async def create_data_scope(obj: CreateDataScopeParam) -> ResponseModel:
    await data_scope_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update data scope',
    dependencies=[
        Depends(RequestPermission('data:scope:edit')),
        DependsRBAC,
    ],
)
async def update_data_scope(
    pk: Annotated[int, Path(description='Data scope ID')], obj: UpdateDataScopeParam
) -> ResponseModel:
    count = await data_scope_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/rules',
    summary='Update data scope rules',
    dependencies=[
        Depends(RequestPermission('data:scope:rule:edit')),
        DependsRBAC,
    ],
)
async def update_data_scope_rules(
    pk: Annotated[int, Path(description='Data scope ID')], rule_ids: UpdateDataScopeRuleParam
):
    count = await data_scope_service.update_data_scope_rule(pk=pk, rule_ids=rule_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='Batch delete data scope',
    dependencies=[
        Depends(RequestPermission('data:scope:del')),
        DependsRBAC,
    ],
)
async def delete_data_scopes(obj: DeleteDataScopeParam) -> ResponseModel:
    count = await data_scope_service.delete(obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
