from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.core.conf import settings
from backend.plugin.code_generator.crud.crud_column import gen_column_dao
from backend.plugin.code_generator.enums import GenMySQLColumnType, GenPostgreSQLColumnType
from backend.plugin.code_generator.model import GenColumn
from backend.plugin.code_generator.schema.column import CreateGenColumnParam, UpdateGenColumnParam
from backend.plugin.code_generator.utils.type_conversion import sql_type_to_pydantic


class GenColumnService:
    """Code generation model column service class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> GenColumn:
        """
        Get the model column with the specified ID

        :param db: database session
        :param pk: model column ID
        :return:
        """

        column = await gen_column_dao.get(db, pk)
        if not column:
            raise errors.NotFoundError(msg='Code generation model column does not exist')
        return column

    @staticmethod
    async def get_types() -> list[str]:
        """Get all column types"""
        if settings.DATABASE_TYPE == 'mysql':
            types = GenMySQLColumnType.get_member_keys()
        else:
            types = GenPostgreSQLColumnType.get_member_keys()
        types.sort()
        return types

    @staticmethod
    async def get_columns(*, db: AsyncSession, business_id: int) -> Sequence[GenColumn]:
        """
        Get all model columns of the specified business

        :param db: database session
        :param business_id: Business ID
        :return:
        """

        return await gen_column_dao.get_all_by_business(db, business_id)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateGenColumnParam) -> None:
        """
        Create model columns

        :param db: database session
        :param obj: Create model column parameters
        :return:
        """

        gen_columns = await gen_column_dao.get_all_by_business(db, obj.gen_business_id)
        if obj.name in [gen_column.name for gen_column in gen_columns]:
            raise errors.ForbiddenError(msg='Model column already exists')

        pd_type = sql_type_to_pydantic(obj.type)
        await gen_column_dao.create(db, obj, pd_type=pd_type)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateGenColumnParam) -> int:
        """
        Update model columns

        :param db: database session
        :param pk: model column ID
        :param obj: Update model column parameters
        :return:
        """

        column = await gen_column_dao.get(db, pk)
        if obj.name != column.name:
            gen_columns = await gen_column_dao.get_all_by_business(db, obj.gen_business_id)
            if obj.name in [gen_column.name for gen_column in gen_columns]:
                raise errors.ConflictError(msg='Model column name already exists')

        pd_type = sql_type_to_pydantic(obj.type)
        return await gen_column_dao.update(db, pk, obj, pd_type=pd_type)

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        Delete model column

        :param db: database session
        :param pk: model column ID
        :return:
        """

        return await gen_column_dao.delete(db, pk)


gen_column_service: GenColumnService = GenColumnService()
