from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.notice.model import Notice
from backend.plugin.notice.schema.notice import CreateNoticeParam, UpdateNoticeParam
from backend.utils.timezone import timezone


class CRUDNotice(CRUDPlus[Notice]):
    """Notification Announcement Database Operation Class"""

    async def get(self, db: AsyncSession, pk: int) -> Notice | None:
        """
        Get notification announcements

        :param db: database session
        :param pk: notification announcement ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_select(self, title: str, type: int | None, status: int | None) -> Select:
        """
        Get notification announcement list query expression

        :param title: Notification announcement title
        :param type: notification announcement type
        :param status: notification announcement status
        :return:
        """
        filters = {'deleted': 0}

        if title is not None:
            filters['title__like'] = f'%{title}%'
        if type is not None:
            filters['type'] = type
        if status is not None:
            filters['status'] = status

        return await self.select_order('created_time', 'desc', **filters)

    async def get_all(self, db: AsyncSession) -> Sequence[Notice]:
        """
        Get all notifications and announcements

        :param db: database session
        :return:
        """
        return await self.select_models(db, deleted=0)

    async def create(self, db: AsyncSession, obj: CreateNoticeParam) -> None:
        """
        Create notification announcement

        :param db: database session
        :param obj: Create notification announcement parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateNoticeParam) -> int:
        """
        Update notification announcement

        :param db: database session
        :param pk: notification announcement ID
        :param obj: update notification announcement parameters
        :return:
        """
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        Bulk deletion notification announcement

        :param db: database session
        :param pks: Notification announcement ID list
        :return:
        """
        return await self.delete_model_by_column(
            db,
            allow_multiple=True,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id__in=pks,
            deleted=0,
        )


notice_dao: CRUDNotice = CRUDNotice(Notice)
