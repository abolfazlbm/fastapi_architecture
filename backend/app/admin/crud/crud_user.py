from collections.abc import Sequence
from typing import Any

import bcrypt

from sqlalchemy import Select, and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig

from backend.app.admin.model import (
    DataRule,
    DataScope,
    Dept,
    Menu,
    Role,
    User,
    data_scope_rule,
    role_data_scope,
    role_menu,
    user_role,
)
from backend.app.admin.schema.user import (
    AddOAuth2UserParam,
    AddUserParam,
    AddUserRoleParam,
    UpdateUserParam,
)
from backend.app.admin.utils.password_security import get_hash_password
from backend.common.enums import StatusType
from backend.common.exception import errors
from backend.plugin.core import check_plugin_installed
from backend.utils.serializers import select_join_serialize
from backend.utils.timezone import timezone


class CRUDUser(CRUDPlus[User]):
    """User database operation class"""

    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        """
        Get user details

        :param db: database session
        :param user_id: User ID
        :return:
        """
        return await self.select_model(db, user_id, deleted=0)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        Get user by username

        :param db: database session
        :param username: username
        :return:
        """
        return await self.select_model_by_column(db, username=username, deleted=0)

    async def get_all_by_usernames(self, db: AsyncSession, usernames: list[str]) -> Sequence[User]:
        """
        通过用户名列表批量获取用户

        :param db: 数据库会话
        :param usernames: 用户名列表
        :return:
        """
        return await self.select_models(db, username__in=usernames, deleted=0)

    async def get_by_nickname(self, db: AsyncSession, nickname: str) -> User | None:
        """
        Get users by nickname

        :param db: database session
        :param nickname: user nickname
        :return:
        """
        return await self.select_model_by_column(db, nickname=nickname, deleted=0)

    async def check_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Check whether the email address has been bound

        :param db: database session
        :param email: email
        :return:
        """
        return await self.select_model_by_column(db, email=email, deleted=0)

    async def get_select(self, dept: int | None, username: str | None, phone: str | None, status: int | None) -> Select:
        """
        Get user list query expression

        :param dept: department ID
        :param username: username
        :param phone: phone number
        :param status: user status
        :return:
        """
        filters = {'deleted': 0}

        if dept:
            filters['dept_id'] = dept
        if username:
            filters['username__like'] = f'%{username}%'
        if phone:
            filters['phone__like'] = f'%{phone}%'
        if status is not None:
            filters['status'] = status

        return await self.select_order(
            'id',
            'desc',
            join_conditions=[
                JoinConfig(
                    model=Dept,
                    join_on=and_(Dept.id == self.model.dept_id, Dept.deleted == 0),
                    fill_result=True,
                ),
                JoinConfig(model=user_role, join_on=user_role.c.user_id == self.model.id),
                JoinConfig(
                    model=Role,
                    join_on=and_(Role.id == user_role.c.role_id, Role.deleted == 0),
                    fill_result=True,
                ),
            ],
            **filters,
        )

    async def add(self, db: AsyncSession, obj: AddUserParam) -> None:
        """
        Add user

        :param db: database session
        :param obj: Add user parameters
        :return:
        """
        salt = bcrypt.gensalt()
        obj.password = get_hash_password(obj.password, salt)

        dict_obj = obj.model_dump(exclude={'roles'})
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)
        db.add(new_user)
        await db.flush()

        if obj.roles:
            role_stmt = select(Role).where(Role.id.in_(obj.roles), Role.deleted == 0)
            result = await db.execute(role_stmt)
            roles = result.scalars().all()

            user_role_data = [AddUserRoleParam(user_id=new_user.id, role_id=role.id).model_dump() for role in roles]
            user_role_stmt = insert(user_role)
            await db.execute(user_role_stmt, user_role_data)

    async def add_by_oauth2(self, db: AsyncSession, obj: AddOAuth2UserParam) -> None:
        """
        Add users via OAuth2

        :param db: database session
        :param obj: Register user parameters
        :return:
        """
        dict_obj = obj.model_dump()
        dict_obj.update({'is_staff': True, 'salt': None})
        new_user = self.model(**dict_obj)
        db.add(new_user)
        await db.flush()

        role_stmt = select(Role).where(Role.status == StatusType.enable, Role.deleted == 0)
        result = await db.execute(role_stmt)
        role = result.scalars().first()  # The first character is bound by default
        if role is None:
            raise errors.NotFoundError(msg='No available roles found, please contact your system administrator')

        user_role_stmt = insert(user_role).values(AddUserRoleParam(user_id=new_user.id, role_id=role.id).model_dump())
        await db.execute(user_role_stmt)

    async def update(self, db: AsyncSession, user_id: int, obj: UpdateUserParam) -> int:
        """
        Update user information

        :param db: database session
        :param user_id: User ID
        :param obj: Update user parameters
        :return:
        """
        role_ids = obj.roles
        del obj.roles

        count = await self.update_model_by_column(db, obj, id=user_id, deleted=0)

        user_role_stmt = delete(user_role).where(user_role.c.user_id == user_id)
        await db.execute(user_role_stmt)

        if role_ids:
            role_stmt = select(Role).where(Role.id.in_(role_ids), Role.deleted == 0)
            result = await db.execute(role_stmt)
            roles = result.scalars().all()

            user_role_data = [AddUserRoleParam(user_id=user_id, role_id=role.id).model_dump() for role in roles]
            user_role_stmt = insert(user_role)
            await db.execute(user_role_stmt, user_role_data)

        return count

    async def update_login_time(self, db: AsyncSession, username: str) -> int:
        """
        Update user's last login time

        :param db: database session
        :param username: username
        :return:
        """
        return await self.update_model_by_column(db, {'last_login_time': timezone.now()}, username=username, deleted=0)

    async def update_password_changed_time(self, db: AsyncSession, user_id: int) -> int:
        """
        Update the user's last password change time

        :param db: database session
        :param user_id: user ID
        :return:
        """
        return await self.update_model_by_column(
            db, {'last_password_changed_time': timezone.now()}, id=user_id, deleted=0
        )

    async def update_nickname(self, db: AsyncSession, user_id: int, nickname: str) -> int:
        """
        Update user nickname

        :param db: database session
        :param user_id: User ID
        :param nickname: user nickname
        :return:
        """
        return await self.update_model_by_column(db, {'nickname': nickname}, id=user_id, deleted=0)

    async def update_avatar(self, db: AsyncSession, user_id: int, avatar: str) -> int:
        """
        Update user avatar

        :param db: database session
        :param user_id: User ID
        :param avatar: avatar address
        :return:
        """
        return await self.update_model_by_column(db, {'avatar': avatar}, id=user_id, deleted=0)

    async def update_email(self, db: AsyncSession, user_id: int, email: str) -> int:
        """
        Update user email

        :param db: database session
        :param user_id: User ID
        :param email: email
        :return:
        """
        return await self.update_model_by_column(db, {'email': email}, id=user_id, deleted=0)

    async def reset_password(self, db: AsyncSession, pk: int, password: str) -> int:
        """
        Reset user password

        :param db: database session
        :param pk: User ID
        :param password: new password
        :return:
        """
        salt = bcrypt.gensalt()
        new_pwd = get_hash_password(password, salt)
        return await self.update_model_by_column(db, {'password': new_pwd, 'salt': salt}, flush=True, id=pk, deleted=0)

    async def set_super(self, db: AsyncSession, user_id: int, *, is_super: bool) -> int:
        """
        Set user super administrator status

        :param db: database session
        :param user_id: User ID
        :param is_super: whether it is a super administrator
        :return:
        """
        return await self.update_model_by_column(db, {'is_superuser': is_super}, id=user_id, deleted=0)

    async def set_staff(self, db: AsyncSession, user_id: int, *, is_staff: bool) -> int:
        """
        Set user background login status

        :param db: database session
        :param user_id: User ID
        :param is_staff: Whether you can log in to the backend
        :return:
        """
        return await self.update_model_by_column(db, {'is_staff': is_staff}, id=user_id, deleted=0)

    async def set_status(self, db: AsyncSession, user_id: int, status: int) -> int:
        """
        Set user status

        :param db: database session
        :param user_id: User ID
        :param status: status
        :return:
        """
        return await self.update_model_by_column(db, {'status': status}, id=user_id, deleted=0)

    async def set_multi_login(self, db: AsyncSession, user_id: int, *, multi_login: bool) -> int:
        """
        Set user multi-terminal login status

        :param db: database session
        :param user_id: User ID
        :param multi_login: Whether to allow multiple logins
        :return:
        """
        return await self.update_model_by_column(db, {'is_multi_login': multi_login}, id=user_id, deleted=0)

    async def delete(self, db: AsyncSession, user_id: int) -> int:
        """
        Delete user

        :param db: database session
        :param user_id: user ID
        :return:
        """
        if check_plugin_installed('oauth2'):
            try:
                from backend.plugin.oauth2.crud.crud_user_social import user_social_dao

                await user_social_dao.delete_by_user_id(db, user_id)
            except ImportError:
                raise errors.ServerError(msg='OAuth2 Plug-in usage failed to import, please contact the system administrator')

        user_role_stmt = delete(user_role).where(user_role.c.user_id == user_id)
        await db.execute(user_role_stmt)

        return await self.delete_model_by_column(
            db,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id=user_id,
            deleted=0,
        )

    async def get_join(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        username: str | None = None,
    ) -> Any | None:
        """
        Get user related information

        :param db: database session
        :param user_id: User ID
        :param username: username
        :return:
        """
        filters = {'deleted': 0}

        if user_id:
            filters['id'] = user_id
        if username:
            filters['username'] = username

        result = await self.select_models(
            db,
            join_conditions=[
                JoinConfig(
                    model=Dept,
                    join_on=and_(Dept.id == self.model.dept_id, Dept.deleted == 0),
                    fill_result=True,
                ),
                JoinConfig(model=user_role, join_on=user_role.c.user_id == self.model.id),
                JoinConfig(
                    model=Role,
                    join_on=and_(Role.id == user_role.c.role_id, Role.deleted == 0),
                    fill_result=True,
                ),
                JoinConfig(model=role_menu, join_on=role_menu.c.role_id == Role.id),
                JoinConfig(
                    model=Menu,
                    join_on=and_(Menu.id == role_menu.c.menu_id, Menu.deleted == 0),
                    fill_result=True,
                ),
                JoinConfig(model=role_data_scope, join_on=role_data_scope.c.role_id == Role.id),
                JoinConfig(
                    model=DataScope,
                    join_on=and_(DataScope.id == role_data_scope.c.data_scope_id, DataScope.deleted == 0),
                    fill_result=True,
                ),
                JoinConfig(model=data_scope_rule, join_on=data_scope_rule.c.data_scope_id == DataScope.id),
                JoinConfig(
                    model=DataRule,
                    join_on=and_(DataRule.id == data_scope_rule.c.data_rule_id, DataRule.deleted == 0),
                    fill_result=True,
                ),
            ],
            **filters,
        )

        return select_join_serialize(
            result,
            relationships=[
                'User-m2o-Dept',
                'User-m2m-Role',
                'Role-m2m-Menu',
                'Role-m2m-DataScope:scopes',
                'DataScope-m2m-DataRule:rules',
            ],
        )


user_dao: CRUDUser = CRUDUser(User)
