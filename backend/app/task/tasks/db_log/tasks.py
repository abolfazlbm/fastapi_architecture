#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from celery import shared_task

from backend.app.admin.service.login_log_service import login_log_service
from backend.app.admin.service.opera_log_service import opera_log_service


@shared_task
async def delete_db_opera_log() -> str:
    """Automatically delete database operation log"""
    await opera_log_service.delete_all()
    return 'Success'


@shared_task
async def delete_db_login_log() -> str:
    """Automatically delete database log"""
    await login_log_service.delete_all()
    return 'Success'
