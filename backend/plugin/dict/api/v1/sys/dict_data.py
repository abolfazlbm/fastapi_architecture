from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.dict.schema.dict_data import (
    CreateDictDataParam,
    DeleteDictDataParam,
    GetDictDataDetail,
    UpdateDictDataParam,
)
from backend.plugin.dict.service.dict_data_service import dict_data_service

router = APIRouter()


@router.get('/all', summary='Get all dictionary data', dependencies=[DependsJwtAuth])
async def get_all_dict_datas(db: CurrentSession) -> ResponseSchemaModel[list[GetDictDataDetail]]:
    data = await dict_data_service.get_all(db=db)
    return response_base.success(data=data)


@router.get('/{pk}', summary='Get dictionary data details', dependencies=[DependsJwtAuth])
async def get_dict_data(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Dictionary Data ID')],
) -> ResponseSchemaModel[GetDictDataDetail]:
    data = await dict_data_service.get(db=db, pk=pk)
    return response_base.success(data=data)


@router.get('/type-codes/{code}', summary='Get dictionary data list', dependencies=[DependsJwtAuth])
async def get_dict_data_by_type_code(
    db: CurrentSession,
    code: Annotated[str, Path(description='Dictionary type encoding')],
) -> ResponseSchemaModel[list[GetDictDataDetail]]:
    data = await dict_data_service.get_by_type_code(db=db, code=code)
    return response_base.success(data=data)


@router.get(
    '',
    summary='Get all dictionary data in pages',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_dict_datas_paginated(
    db: CurrentSession,
    type_code: Annotated[str | None, Query(description='Dictionary type encoding')] = None,
    label: Annotated[str | None, Query(description='Dictionary data label')] = None,
    value: Annotated[str | None, Query(description='Dictionary data key value')] = None,
    status: Annotated[int | None, Query(description='Status')] = None,
    type_id: Annotated[int | None, Query(description='Dictionary type ID')] = None,
) -> ResponseSchemaModel[PageData[GetDictDataDetail]]:
    page_data = await dict_data_service.get_list(
        db=db,
        type_code=type_code,
        label=label,
        value=value,
        status=status,
        type_id=type_id,
    )
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='Create dictionary data',
    dependencies=[
        Depends(RequestPermission('dict:data:add')),
        DependsRBAC,
    ],
)
async def create_dict_data(db: CurrentSessionTransaction, obj: CreateDictDataParam) -> ResponseModel:
    await dict_data_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update dictionary data',
    dependencies=[
        Depends(RequestPermission('dict:data:edit')),
        DependsRBAC,
    ],
)
async def update_dict_data(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Dictionary data ID')],
    obj: UpdateDictDataParam,
) -> ResponseModel:
    count = await dict_data_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='Delete dictionary data in batches',
    dependencies=[
        Depends(RequestPermission('dict:data:del')),
        DependsRBAC,
    ],
)
async def delete_dict_datas(db: CurrentSessionTransaction, obj: DeleteDictDataParam) -> ResponseModel:
    count = await dict_data_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
