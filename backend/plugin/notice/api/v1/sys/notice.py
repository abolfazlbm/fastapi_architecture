from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.notice.schema.notice import (
    CreateNoticeParam,
    DeleteNoticeParam,
    GetNoticeDetail,
    UpdateNoticeParam,
)
from backend.plugin.notice.service.notice_service import notice_service

router = APIRouter()

@router.get('/{pk}', summary='Get notification announcement details', dependencies=[DependsJwtAuth])
async def get_notice(
    db: CurrentSession, pk: Annotated[int, Path(description='Notification Announcement ID')]
) -> ResponseSchemaModel[GetNoticeDetail]:
    notice = await notice_service.get(db=db, pk=pk)
    return response_base.success(data=notice)


@router.get(
    '',
    summary='Get all notification announcements in pages',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_notices_paginated(
    db: CurrentSession,
    title: Annotated[str | None, Query(description='title')] = None,
    type: Annotated[int | None, Query(description='type')] = None,
    status: Annotated[int | None, Query(description='status')] = None,
) -> ResponseSchemaModel[PageData[GetNoticeDetail]]:
    page_data = await notice_service.get_list(db=db, title=title, type=type, status=status)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='Create notification announcement',
    dependencies=[
        Depends(RequestPermission('sys:notice:add')),
        DependsRBAC,
    ],
)
async def create_notice(db: CurrentSessionTransaction, obj: CreateNoticeParam) -> ResponseModel:
    await notice_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='Update notification announcement',
    dependencies=[
        Depends(RequestPermission('sys:notice:edit')),
        DependsRBAC,
    ],
)
async def update_notice(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='Notices and Announcements ID')], obj: UpdateNoticeParam
) -> ResponseModel:
    count = await notice_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='Bulk deletion notification announcement',
    dependencies=[
        Depends(RequestPermission('sys:notice:del')),
        DependsRBAC,
    ],
)
async def delete_notices(db: CurrentSessionTransaction, obj: DeleteNoticeParam) -> ResponseModel:
    count = await notice_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
