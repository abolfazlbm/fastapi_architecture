from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.oauth2.model import UserSocial
from backend.plugin.oauth2.schema.user_social import CreateUserSocialParam


class CRUDUserSocial(CRUDPlus[UserSocial]):
    """User social account database operation class"""

    async def check_binding(self, db: AsyncSession, user_id: int, source: str) -> UserSocial | None:
        """
        Check system user social account binding

        :param db: database session
        :param user_id: User ID
        :param source: social account type
        :return:
        """
        return await self.select_model_by_column(db, user_id=user_id, source=source)

    async def get_by_sid(self, db: AsyncSession, sid: str, source: str) -> UserSocial | None:
        """
        Get social user by sid

        :param db: database session
        :param sid: unique code of social account
        :param source: social account type
        :return:
        """
        return await self.select_model_by_column(db, sid=sid, source=source)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Sequence[UserSocial]:
        """
        Get all social account bindings by user ID

        :param db: database session
        :param user_id: user ID
        :return:
        """
        return await self.select_models(db, user_id=user_id)

    async def create(self, db: AsyncSession, obj: CreateUserSocialParam) -> None:
        """
        Create user social account binding

        :param db: database session
        :param obj: Create user social account binding parameters
        :return:
        """
        await self.create_model(db, obj)

    async def delete(self, db: AsyncSession, user_id: int, source: str) -> int:
        """
        Delete user social account binding

        :param db: database session
        :param user_id: user ID
        :param source: social account type
        :return:
        """
        return await self.delete_model_by_column(db, user_id=user_id, source=source)

    async def delete_by_user_id(self, db: AsyncSession, user_id: int) -> int:
        """
        Delete user social by user ID

        :param db: database session
        :param user_id: user ID
        :return:
        """
        return await self.delete_model_by_column(db, user_id=user_id)


user_social_dao: CRUDUserSocial = CRUDUserSocial(UserSocial)
