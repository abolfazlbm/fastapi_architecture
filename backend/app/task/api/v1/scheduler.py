#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.task.schema.scheduler import CreateTaskSchedulerParam, GetTaskSchedulerDetail, UpdateTaskSchedulerParam
from backend.app.task.service.scheduler_service import task_scheduler_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('/all', summary='get all task schedules', dependencies=[DependsJwtAuth])
async def get_all_task_schedulers() -> ResponseSchemaModel[list[GetTaskSchedulerDetail]]:
    schedulers = await task_scheduler_service.get_all()
    return response_base.success(data=schedulers)


@router.get('/{pk}', summary='get task scheduling details', dependencies=[DependsJwtAuth])
async def get_task_scheduler(
    pk: Annotated[int, Path(description='Task schedule ID')],
) -> ResponseSchemaModel[GetTaskSchedulerDetail]:
    task_scheduler = await task_scheduler_service.get(pk=pk)
    return response_base.success(data=task_scheduler)


@router.get(
    '',
    summary='Pagination gets all task schedules',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_task_scheduler_paged(
    db: CurrentSession,
    name: Annotated[int, Path(description='Task schedule name')] = None,
    type: Annotated[int | None, Query(description='Task scheduling type')] = None,
) -> ResponseSchemaModel[PageData[GetTaskSchedulerDetail]]:
    task_scheduler_select = await task_scheduler_service.get_select(name=name, type=type)
    page_data = await paging_data(db, task_scheduler_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='Create task schedule',
    dependencies=[
        Depends(RequestPermission('sys:task:add')),
        DependsRBAC,
    ],
)
async def create_task_scheduler(obj: CreateTaskSchedulerParam) -> ResponseModel:
    await task_scheduler_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update task scheduling',
    dependencies=[
        Depends(RequestPermission('sys:task:edit')),
        DependsRBAC,
    ],
)
async def update_task_scheduler(
    pk: Annotated[int, Path(description='Task scheduling ID')], obj: UpdateTaskSchedulerParam
) -> ResponseModel:
    count = await task_scheduler_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='Update task scheduling status',
    dependencies=[
        Depends(RequestPermission('sys:task:edit')),
        DependsRBAC,
    ],
)
async def update_task_scheduler_status(pk: Annotated[int, Path(description='Task schedule ID')]) -> ResponseModel:
    count = await task_scheduler_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='Delete task schedule',
    dependencies=[
        Depends(RequestPermission('sys:task:del')),
        DependsRBAC,
    ],
)
async def delete_task_scheduler(pk: Annotated[int, Path(description='Task Scheduling ID')]) -> ResponseModel:
    count = await task_scheduler_service.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.post(
    '/{pk}/executions',
    summary='Execute tasks manually',
    dependencies=[
        Depends(RequestPermission('sys:task:exec')),
        DependsRBAC,
    ],
)
async def execute_task(pk: Annotated[int, Path(description='Task schedule ID')]) -> ResponseModel:
    await task_scheduler_service.execute(pk=pk)
    return response_base.success()
