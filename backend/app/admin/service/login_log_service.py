#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from fastapi import Request
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.crud.crud_login_log import login_log_dao
from backend.app.admin.schema.login_log import CreateLoginLogParam, DeleteLoginLogParam
from backend.common.log import log
from backend.database.db import async_db_session


class LoginLogService:
    """Login log service class"""

    @staticmethod
    async def get_select(*, username: str | None, status: int | None, ip: str | None) -> Select:
        """
        Get the login log list query conditions

        :param username: Username
        :param status: status
        :param ip: IP address
        :return:
        """
        return await login_log_dao.get_list(username=username, status=status, ip=ip)

    @staticmethod
    async def create(
        *,
        db: AsyncSession,
        request: Request,
        user_uuid: str,
        username: str,
        login_time: datetime,
        status: int,
        msg: str,
    ) -> None:
        """
        Create a login log

        :param db: database session
        :param request: FastAPI request object
        :param user_uuid: User UUID
        :param username: Username
        :param login_time: login time
        :param status: status
        :param msg: message
        :return:
        """
        try:
            obj = CreateLoginLogParam(
                user_uuid=user_uuid,
                username=username,
                status=status,
                ip=request.state.ip,
                country=request.state.country,
                region=request.state.region,
                city=request.state.city,
                user_agent=request.state.user_agent,
                browser=request.state.browser,
                os=request.state.os,
                device=request.state.device,
                msg=msg,
                login_time=login_time,
            )
            await login_log_dao.create(db, obj)
        except Exception as e:
            log.error(f'Login log creation failed: {e}')

    @staticmethod
    async def delete(*, obj: DeleteLoginLogParam) -> int:
        """
        Batch delete login

        :param obj: Log ID list
        :return:
        """
        async with async_db_session.begin() as db:
            count = await login_log_dao.delete(db, obj.pks)
            return count

    @staticmethod
    async def delete_all() -> None:
        """Clear all login logs"""
        async with async_db_session.begin() as db:
            await login_log_dao.delete_all(db)


login_log_service: LoginLogService = LoginLogService()
