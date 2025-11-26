from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.notice.crud.crud_notice import notice_dao
from backend.plugin.notice.model import Notice
from backend.plugin.notice.schema.notice import CreateNoticeParam, DeleteNoticeParam, UpdateNoticeParam


class NoticeService:
    """Notification and Announcement Service"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Notice:
        """
        Get notification announcements

        :param db: database session
        :param pk: notification announcement ID
        :return:
        """

        notice = await notice_dao.get(db, pk)
        if not notice:
            raise errors.NotFoundError(msg='Notification announcement does not exist')
        return notice

    @staticmethod
    async def get_list(db: AsyncSession, title: str | None, type: int | None, status: int | None) -> dict[str, Any]:
        """
        Get notification announcement list

        :param db: database session
        :param title: Notification announcement title
        :param type: notification announcement type
        :param status: notification announcement status
        :return:
        """
        notice_select = await notice_dao.get_select(title, type, status)
        return await paging_data(db, notice_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[Notice]:
        """
        Get all notifications and announcements

        :param db: database session
        :return:
        """

        notices = await notice_dao.get_all(db)
        return notices

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateNoticeParam) -> None:
        """
        Create notification announcement

        :param db: database session
        :param obj: Create notification announcement parameters
        :return:
        """

        await notice_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateNoticeParam) -> int:
        """
        Update notification announcement

        :param db: database session
        :param pk: notification announcement ID
        :param obj: update notification announcement parameters
        :return:
        """

        notice = await notice_dao.get(db, pk)
        if not notice:
            raise errors.NotFoundError(msg='Notification announcement does not exist')
        count = await notice_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteNoticeParam) -> int:
        """
        Bulk deletion notification announcement

        :param db: database session
        :param obj: Notification announcement ID list
        :return:
        """

        count = await notice_dao.delete(db, obj.pks)
        return count


notice_service: NoticeService = NoticeService()
