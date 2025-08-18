#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import MenuType, StatusType
from backend.common.schema import SchemaBase


class MenuSchemaBase(SchemaBase):
    """Menu Basic Model"""

    title: str = Field(description='Menu title')
    name: str = Field(description='Menu name')
    path: str | None = Field(None, description='Route Address')
    parent_id: int | None = Field(None, description='Men Parent ID')
    sort: int = Field(0, ge=0, description='Sort')
    icon: str | None = Field(None, description='icon')
    type: MenuType = Field(description='Menu Type (0 directory 1 menu 2 buttons 3 embedded 4 external links)')
    component: str | None = Field(None, description='Component Path')
    perms: str | None = Field(None, description='Permission Identification')
    status: StatusType = Field(description='Status')
    display: StatusType = Field(description='Does it be displayed')
    cache: StatusType = Field(description='Cache or not')
    link: str | None = Field(None, description='Outline link address')
    remark: str | None = Field(None, description='Remark')


class CreateMenuParam(MenuSchemaBase):
    """Create menu parameters"""


class UpdateMenuParam(MenuSchemaBase):
    """Update menu parameters"""


class GetMenuDetail(MenuSchemaBase):
    """Menu Details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Menu ID')
    created_time: datetime = Field(description='Create time')
    updated_time: datetime | None = Field(None, description='Update time')
