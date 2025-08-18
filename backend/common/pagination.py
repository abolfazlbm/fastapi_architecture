#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar

from fastapi import Depends, Query
from fastapi_pagination import pagination_ctx
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_pagination.links.bases import create_links
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')
SchemaT = TypeVar('SchemaT')


class _CustomPageParams(BaseModel, AbstractParams):
    """Custom paging parameters"""

    page: int = Query(1, ge=1, description='page number')
    size: int = Query(20, gt=0, le=200, description='Number of per page')

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class _Links(BaseModel):
    """Pagination link"""

    first: str = Field(description='Homepage link')
    last: str = Field(description='Last page link')
    self: str = Field(description='Current page link')
    next: str | None = Field(None, description='Next page link')
    prev: str | None = Field(None, description='Previous page link')


class _PageDetails(BaseModel):
    """Pagination details"""

    items: list = Field([], description='Current page data list')
    total: int = Field(description='Total number of data')
    page: int = Field(description='Current page number')
    size: int = Field(description='number per page')
    total_pages: int = Field(description='Total Pages')
    links: _Links = Field(description='Pagination Link')


class _CustomPage(_PageDetails, AbstractPage[T], Generic[T]):
    """Custom paging class"""

    __params_type__ = _CustomPageParams

    @classmethod
    def create(
        cls,
        items: list,
        params: _CustomPageParams,
        total: int = 0,
    ) -> _CustomPage[T]:
        page = params.page
        size = params.size
        total_pages = ceil(total / size)
        links = create_links(
            first={'page': 1, 'size': size},
            last={'page': total_pages, 'size': size} if total > 0 else {'page': 1, 'size': size},
            next={'page': page + 1, 'size': size} if (page + 1) <= total_pages else None,
            prev={'page': page - 1, 'size': size} if (page - 1) >= 1 else None,
        ).model_dump()

        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            links=links,  # type: ignore
        )


class PageData(_PageDetails, Generic[SchemaT]):
    """
    Unified return model containing return data schema, only for pagination interfaces

    E.g. ::

        @router.get('/test', response_model=ResponseSchemaModel[PageData[GetApiDetail]])
        def test():
            return ResponseSchemaModel[PageData[GetApiDetail]](data=GetApiDetail(...))


        @router.get('/test')
        def test() -> ResponseSchemaModel[PageData[GetApiDetail]]:
            return ResponseSchemaModel[PageData[GetApiDetail]](data=GetApiDetail(...))


        @router.get('/test')
        def test() -> ResponseSchemaModel[PageData[GetApiDetail]]:
            res = CustomResponseCode.HTTP_200
            return ResponseSchemaModel[PageData[GetApiDetail]](code=res.code, msg=res.msg, data=GetApiDetail(...))
    """

    items: Sequence[SchemaT]


async def paging_data(db: AsyncSession, select: Select) -> dict[str, Any]:
    """
    Create paging data based on SQLAlchemy

    :param db: database session
    :param select: SQL query statement
    :return:
    """
    paginated_data: _CustomPage = await apaginate(db, select)
    page_data = paginated_data.model_dump()
    return page_data


# Pagination dependency injection
DependsPagination = Depends(pagination_ctx(_CustomPage))
