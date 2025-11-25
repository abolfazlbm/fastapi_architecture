from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.crud.crud_dept import dept_dao
from backend.app.admin.model import Dept
from backend.app.admin.schema.dept import CreateDeptParam, UpdateDeptParam
from backend.app.admin.schema.user import GetUserInfoWithRelationDetail
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.build_tree import get_tree_data


class DeptService:
    """Departmental Services"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> Dept:
        """
        Get department details

        :param db: 数据库会话
        :param pk: Department ID
        :return:
        """

        dept = await dept_dao.get(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='Does not exist')
        return dept

    @staticmethod
    async def get_tree(
        *,
        db: AsyncSession,
        request_user: GetUserInfoWithRelationDetail,
        name: str | None,
        leader: str | None,
        phone: str | None,
        status: int | None,
    ) -> list[dict[str, Any]]:
        """
        Obtain department tree structure

        :param db: database session
        :param request_user: request user
        :param name: department name
        :param leader: department head
        :param phone: Contact number
        :param status: status
        :return:
        """

        dept_select = await dept_dao.get_all(db, request_user, name, leader, phone, status)
        tree_data = get_tree_data(dept_select)
        return tree_data

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDeptParam) -> None:
        """
        Create a department

        :param db: database session
        :param obj: Department creation parameters
        :return:
        """
        dept = await dept_dao.get_by_name(db, obj.name)
        if dept:
            raise errors.ConflictError(msg='Department name already exists')
        if obj.parent_id is not None:
            parent_dept = await dept_dao.get(db, obj.parent_id)
            if not parent_dept:
                raise errors.NotFoundError(msg='The parent department does not exist')
        await dept_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDeptParam) -> int:
        """
        Update department

        :param db: database session
        :param pk: Department ID
        :param obj: Department update parameters
        :return:
        """
        dept = await dept_dao.get(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='Does not exist')
        if dept.name != obj.name and await dept_dao.get_by_name(db, obj.name):
            raise errors.ConflictError(msg='Department name already exists')
        if obj.parent_id:
            parent_dept = await dept_dao.get(db, obj.parent_id)
            if not parent_dept:
                raise errors.NotFoundError(msg='The parent department does not exist')
        if obj.parent_id == dept.id:
            raise errors.ForbiddenError(msg='Prohibit association itself as parent')
        count = await dept_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        Delete the department

        :param db: database session
        :param pk: Department ID
        :return:
        """
        dept = await dept_dao.get_join(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='Department does not exist')
        if dept.users:
            raise errors.ConflictError(msg='There is a user under the department, it cannot be deleted')
        children = await dept_dao.get_children(db, pk)
        if children:
            raise errors.ConflictError(msg='There is a sub-department under the department, and it cannot be deleted')
        count = await dept_dao.delete(db, pk)
        for user in dept.users:
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}')
        return count

dept_service: DeptService = DeptService()
