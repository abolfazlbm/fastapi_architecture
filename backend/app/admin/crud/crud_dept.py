from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig

from backend.app.admin.model import Dept, User
from backend.app.admin.schema.dept import CreateDeptParam, UpdateDeptParam
from backend.app.admin.schema.user import GetUserInfoWithRelationDetail
from backend.common.security.permission import filter_data_permission
from backend.utils.serializers import select_join_serialize


class CRUDDept(CRUDPlus[Dept]):
    """Departmental Database Operation Class"""

    async def get(self, db: AsyncSession, dept_id: int) -> Dept | None:
        """
        Get department details

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.select_model_by_column(db, id=dept_id, del_flag=False)

    async def get_by_name(self, db: AsyncSession, name: str) -> Dept | None:
        """
        Get department by name

        :param db: database session
        :param name: department name
        :return:
        """
        return await self.select_model_by_column(db, name=name, del_flag=False)

    async def get_all(
        self,
        db: AsyncSession,
        request_user: GetUserInfoWithRelationDetail,
        name: str | None,
        leader: str | None,
        phone: str | None,
        status: int | None,
    ) -> Sequence[Dept]:
        """
        Get all departments

        :param db: database session
        :param request_user: request user
        :param name: department name
        :param leader: person in charge
        :param phone: Contact number
        :param status: department status
        :return:
        """
        filters = {'del_flag': False}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if leader is not None:
            filters['leader__like'] = f'%{leader}%'
        if phone is not None:
            filters['phone__startswith'] = phone
        if status is not None:
            filters['status'] = status

        data_filter = filter_data_permission(request_user)
        return await self.select_models_order(db, 'sort', 'desc', data_filter, **filters)

    async def create(self, db: AsyncSession, obj: CreateDeptParam) -> None:
        """
        Create a department

        :param db: database session
        :param obj: Create department parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, dept_id: int, obj: UpdateDeptParam) -> int:
        """
        Update department

        :param db: database session
        :param dept_id: Department ID
        :param obj: Update department parameters
        :return:
        """
        return await self.update_model(db, dept_id, obj)

    async def delete(self, db: AsyncSession, dept_id: int) -> int:
        """
        Delete the department

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.delete_model_by_column(db, id=dept_id, logical_deletion=True, deleted_flag_column='del_flag')

    async def get_join(self, db: AsyncSession, dept_id: int) -> Any | None:
        """
        Obtain department and related data

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        result = await self.select_model(
            db,
            dept_id,
            join_conditions=[JoinConfig(model=User, join_on=User.dept_id == self.model.id, fill_result=True)],
        )
        return select_join_serialize(result, relationships=['Dept-o2m-User'])

    async def get_children(self, db: AsyncSession, dept_id: int) -> Sequence[Dept | None]:
        """
        Get a list of sub-departments

        :param db: database session
        :param dept_id: Department ID
        :return:
        """
        return await self.select_models(db, parent_id=dept_id, del_flag=False)

dept_dao: CRUDDept = CRUDDept(Dept)
