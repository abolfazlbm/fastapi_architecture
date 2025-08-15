# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.sys.data_rule import router as data_rule_router
from backend.app.admin.api.v1.sys.data_scope import router as data_scope_router
from backend.app.admin.api.v1.sys.dept import router as dept_router
from backend.app.admin.api.v1.sys.files import router as file_router
from backend.app.admin.api.v1.sys.menu import router as menu_router
from backend.app.admin.api.v1.sys.plugin import router as plugin_router
from backend.app.admin.api.v1.sys.role import router as role_router
from backend.app.admin.api.v1.sys.user import router as user_router

router = APIRouter(prefix='/sys')

router.include_router(dept_router, prefix='/depts', tags=['System Department'])
router.include_router(menu_router, prefix='/menus', tags=['System Menu'])
router.include_router(role_router, prefix='/roles', tags=['System Role'])
router.include_router(user_router, prefix='/users', tags=['System User'])
router.include_router(data_rule_router, prefix='/data-rules', tags=['System Data Rules'])
router.include_router(data_scope_router, prefix='/data-scopes', tags=['System Data Range'])
router.include_router(file_router, prefix='/files', tags=['System File'])
router.include_router(plugin_router, prefix='/plugins', tags=['System Plugin'])
