from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.code_generator.model import GenColumn
from backend.plugin.code_generator.schema.column import CreateGenColumnParam, UpdateGenColumnParam


class CRUDGenColumn(CRUDPlus[GenColumn]):
    """Code generation model column CRUD class"""

    async def get(self, db: AsyncSession, pk: int) -> GenColumn | None:
        """
        Get code generation model columns

        :param db: database session
        :param pk: code generation model ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_all_by_business(self, db: AsyncSession, business_id: int) -> Sequence[GenColumn]:
        """
        Get all code generation model columns

        :param db: database session
        :param business_id: Business ID
        :return:
        """
        return await self.select_models_order(db, sort_columns='sort', gen_business_id=business_id)

    async def create(self, db: AsyncSession, obj: CreateGenColumnParam, pd_type: str | None) -> None:
        """
        Create code generation model columns

        :param db: database session
        :param obj: Create code generation model column parameters
        :param pd_type: Pydantic type
        :return:
        """
        await self.create_model(db, obj, pd_type=pd_type)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateGenColumnParam, pd_type: str | None) -> int:
        """
        Update code generation model columns

        :param db: database session
        :param pk: code generation model column ID
        :param obj: Update code generation model column parameters
        :param pd_type: Pydantic type
        :return:
        """
        return await self.update_model(db, pk, obj, pd_type=pd_type)

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """
        Remove code generation model columns

        :param db: database session
        :param pk: code generation model column ID
        :return:
        """
        return await self.delete_model(db, pk)


gen_column_dao: CRUDGenColumn = CRUDGenColumn(GenColumn)
