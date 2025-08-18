#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from typing import Sequence

from fastapi import Request
from sqlalchemy import Select

from backend.app.admin.crud.crud_dept import dept_dao
from backend.app.admin.crud.crud_role import role_dao
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.model import Role, User
from backend.app.admin.schema.user import (
    AddUserParam,
    ResetPasswordParam,
    UpdateUserParam,
)
from backend.common.enums import UserPermissionType
from backend.common.exception import errors
from backend.common.response.response_code import CustomErrorCode
from backend.common.security.jwt import get_token, jwt_decode, password_verify, superuser_verify
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client


class UserService:
    """User Service Class"""

    @staticmethod
    async def get_userinfo(*, pk: int | None = None, username: str | None = None) -> User:
        """
        Get user information

        :param pk: User ID
        :param username: Username
        :return:
        """
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, user_id=pk, username=username)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            return user

    @staticmethod
    async def get_roles(*, pk: int) -> Sequence[Role]:
        """
        Get all roles of users

        :param pk: User ID
        :return:
        """
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, user_id=pk)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            return user.roles

    @staticmethod
    async def get_select(*, dept: int, username: str, phone: str, status: int) -> Select:
        """
        Get user list query conditions

        :param dept: Department ID
        :param username: Username
        :param phone: mobile phone number
        :param status: status
        :return:
        """
        return await user_dao.get_list(dept=dept, username=username, phone=phone, status=status)

    @staticmethod
    async def create(*, request: Request, obj: AddUserParam) -> None:
        """
        Create a user

        :param request: FastAPI request object
        :param obj: User adds parameters
        :return:
        """
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if await user_dao.get_by_username(db, obj.username):
                raise errors.ConflictError(msg='Username registered')
            obj.nickname = obj.nickname if obj.nickname else f'#{random.randrange(88888, 99999)}'
            if not obj.password:
                raise errors.RequestError(msg='Password is not allowed to be empty')
            if not await dept_dao.get(db, obj.dept_id):
                raise errors.NotFoundError(msg='Does not exist')
            for role_id in obj.roles:
                if not await role_dao.get(db, role_id):
                    raise errors.NotFoundError(msg='role does not exist')
            await user_dao.add(db, obj)

    @staticmethod
    async def update(*, request: Request, pk: int, obj: UpdateUserParam) -> int:
        """
        更新用户信息

        :param request: FastAPI 请求对象
        :param pk: User ID
        :param obj: 用户更新参数
        :return:
        """
        async with async_db_session.begin() as db:
            superuser_verify(request)
            user = await user_dao.get_with_relation(db, user_id=pk)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            if obj.username != user.username:
                if await user_dao.get_by_username(db, obj.username):
                    raise errors.ConflictError(msg='用户名已注册')
            for role_id in obj.roles:
                if not await role_dao.get(db, role_id):
                    raise errors.NotFoundError(msg='角色不存在')
            count = await user_dao.update(db, user, obj)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_permission(*, request: Request, pk: int, type: UserPermissionType) -> int:
        """
        Update user permissions

        :param request: FastAPI request object
        :param pk: User ID
        :param type: permission type
        :return:
        """
        async with async_db_session.begin() as db:
            superuser_verify(request)
            match type:
                case UserPermissionType.superuser:
                    user = await user_dao.get(db, pk)
                    if not user:
                        raise errors.NotFoundError(msg='user does not exist')
                    if pk == request.user.id:
                        raise errors.ForbiddenError(msg='Change changes to its own permissions')
                    count = await user_dao.set_super(db, pk, not user.status)
                case UserPermissionType.staff:
                    user = await user_dao.get(db, pk)
                    if not user:
                        raise errors.NotFoundError(msg='user does not exist')
                    if pk == request.user.id:
                        raise errors.ForbiddenError(msg='Change changes to its own permissions')
                    count = await user_dao.set_staff(db, pk, not user.is_staff)
                case UserPermissionType.status:
                    user = await user_dao.get(db, pk)
                    if not user:
                        raise errors.NotFoundError(msg='user does not exist')
                    if pk == request.user.id:
                        raise errors.ForbiddenError(msg='Change changes to its own permissions')
                    count = await user_dao.set_status(db, pk, 0 if user.status == 1 else 1)
                case UserPermissionType.multi_login:
                    user = await user_dao.get(db, pk)
                    if not user:
                        raise errors.NotFoundError(msg='user does not exist')
                    multi_login = user.is_multi_login if pk != user.id else request.user.is_multi_login
                    new_multi_login = not multi_login
                    count = await user_dao.set_multi_login(db, pk, new_multi_login)
                    token = get_token(request)
                    token_payload = jwt_decode(token)
                    if pk == user.id:
                        # When the system administrator modifys itself, other tokens except the current token are invalid
                        if not new_multi_login:
                            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{user.id}'
                            await redis_client.delete_prefix(
                                key_prefix, exclude=f'{key_prefix}:{token_payload.session_uuid}'
                            )
                    else:
                        # When the system administrator modifies others, all other tokens are invalid
                        if not new_multi_login:
                            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{user.id}'
                            await redis_client.delete_prefix(key_prefix)
                case _:
                    raise errors.RequestError(msg='Permission type does not exist')

        await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
        return count

    @staticmethod
    async def reset_password(*, request: Request, pk: int, password: str) -> int:
        """
        Reset user password

        :param request: FastAPI request object
        :param pk: User ID
        :param password: new password
        :return:
        """
        async with async_db_session.begin() as db:
            superuser_verify(request)
            user = await user_dao.get(db, pk)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            count = await user_dao.reset_password(db, user.id, password)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}',
            ]
            for prefix in key_prefix:
                await redis_client.delete(prefix)
            return count

    @staticmethod
    async def update_nickname(*, request: Request, nickname: str) -> int:
        """
        Update the current user nickname

        :param request: FastAPI request object
        :param nickname: user nickname
        :return:
        """
        async with async_db_session.begin() as db:
            token = get_token(request)
            token_payload = jwt_decode(token)
            user = await user_dao.get(db, token_payload.id)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            count = await user_dao.update_nickname(db, token_payload.id, nickname)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_avatar(*, request: Request, avatar: str) -> int:
        """
        Update the current user avatar

        :param request: FastAPI request object
        :param avatar: avatar address
        :return:
        """
        async with async_db_session.begin() as db:
            token = get_token(request)
            token_payload = jwt_decode(token)
            user = await user_dao.get(db, token_payload.id)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            count = await user_dao.update_avatar(db, token_payload.id, avatar)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_email(*, request: Request, captcha: str, email: str) -> int:
        """
        Update the current user's email address

        :param request: FastAPI request object
        :param captcha: Email verification code
        :param email: Email
        :return:
        """
        async with async_db_session.begin() as db:
            token = get_token(request)
            token_payload = jwt_decode(token)
            user = await user_dao.get(db, token_payload.id)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            captcha_code = await redis_client.get(f'{settings.EMAIL_CAPTCHA_REDIS_PREFIX}:{request.state.ip}')
            if not captcha_code:
                raise errors.RequestError(msg='Verification code has expired, please re-get it')
            if captcha != captcha_code:
                raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
            await redis_client.delete(f'{settings.EMAIL_CAPTCHA_REDIS_PREFIX}:{request.state.ip}')
            count = await user_dao.update_email(db, token_payload.id, email)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
            return count

    @staticmethod
    async def update_password(*, request: Request, obj: ResetPasswordParam) -> int:
        """
        Update the current user password

        :param request: FastAPI request object
        :param obj: Password reset parameters
        :return:
        """
        async with async_db_session.begin() as db:
            token = get_token(request)
            token_payload = jwt_decode(token)
            user = await user_dao.get(db, token_payload.id)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            if not password_verify(obj.old_password, user.password):
                raise errors.RequestError(msg='original password error')
            if obj.new_password != obj.confirm_password:
                raise errors.RequestError(msg='Password input is inconsistent')
            count = await user_dao.reset_password(db, user.id, obj.new_password)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}',
            ]
            for prefix in key_prefix:
                await redis_client.delete_prefix(prefix)
            return count

    @staticmethod
    async def delete(*, pk: int) -> int:
        """
        Delete users

        :param pk: User ID
        :return:
        """
        async with async_db_session.begin() as db:
            user = await user_dao.get(db, pk)
            if not user:
                raise errors.NotFoundError(msg='user does not exist')
            count = await user_dao.delete(db, user.id)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count


user_service: UserService = UserService()
