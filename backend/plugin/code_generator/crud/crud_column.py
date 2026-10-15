from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.code_generator.model import CodeGenColumn
from backend.plugin.code_generator.schema.column import (
    CreateCodeGenColumnInternalParam,
    CreateCodeGenColumnParam,
    UpdateCodeGenColumnParam,
)


class CRUDCodeGenColumn(CRUDPlus[CodeGenColumn]):
    """Code generation model column CRUD class"""

    async def get(self, db: AsyncSession, pk: int) -> CodeGenColumn | None:
        """
        Get code generation model columns

        :param db: database session
        :param pk: code generation model ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_all_by_business(self, db: AsyncSession, business_id: int) -> Sequence[CodeGenColumn]:
        """
        Get all code generation model columns

        :param db: database session
        :param business_id: Business ID
        :return:
        """
        return await self.select_models_order(db, sort_columns='sort', code_gen_business_id=business_id)

    async def create(self, db: AsyncSession, obj: CreateCodeGenColumnParam, pd_type: str | None) -> None:
        """
        Create code generation model columns

        :param db: database session
        :param obj: Create code generation model column parameters
        :param pd_type: Pydantic type
        :return:
        """
        await self.create_model(db, obj, pd_type=pd_type)

    async def bulk_create(self, db: AsyncSession, objs: list[CreateCodeGenColumnInternalParam]) -> None:
        """
        Create code generation model columns in batches

        :param db: Database session
        :param objs: List of parameters for creating code generation model columns
        :return:
        """
        await self.create_models(db, objs)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateCodeGenColumnParam, pd_type: str | None) -> int:
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


code_gen_column_dao: CRUDCodeGenColumn = CRUDCodeGenColumn(CodeGenColumn)
