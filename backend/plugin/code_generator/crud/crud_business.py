from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.code_generator.model import GenBusiness
from backend.plugin.code_generator.schema.business import CreateGenBusinessParam, UpdateGenBusinessParam
from backend.utils.timezone import timezone


class CRUDGenBusiness(CRUDPlus[GenBusiness]):
    """Code generation business CRUD classes"""

    async def get(self, db: AsyncSession, pk: int) -> GenBusiness | None:
        """
        Get a code generation business

        :param db: database session
        :param pk: code generation business ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_by_name(self, db: AsyncSession, name: str) -> GenBusiness | None:
        """
        Get code generation business by name

        :param db: database session
        :param name: table name
        :return:
        """
        return await self.select_model_by_column(db, table_name=name, deleted=0)

    async def get_all(self, db: AsyncSession) -> Sequence[GenBusiness]:
        """
        Get all code generation business

        :param db: database session
        :return:
        """
        return await self.select_models(db, deleted=0)

    async def get_select(self, table_name: str | None) -> Select:
        """
        Get all code generation business query expressions

        :param table_name: business table name
        :return:
        """
        filters = {'deleted': 0}

        if table_name is not None:
            filters['table_name__like'] = f'%{table_name}%'

        return await self.select_order('id', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateGenBusinessParam) -> None:
        """
        Create a code generation business

        :param db: database session
        :param obj: Create code generation business parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateGenBusinessParam) -> int:
        """
        Update code generation business

        :param db: database session
        :param pk: code generation business ID
        :param obj: Update code generation business parameters
        :return:
        """
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """
        Remove code generation business

        :param db: database session
        :param pk: code generation business ID
        :return:
        """
        return await self.delete_model_by_column(
            db,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id=pk,
            deleted=0,
        )


gen_business_dao: CRUDGenBusiness = CRUDGenBusiness(GenBusiness)
