from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.code_generator.crud.crud_business import code_gen_business_dao
from backend.plugin.code_generator.model import CodeGenBusiness
from backend.plugin.code_generator.schema.business import CreateCodeGenBusinessParam, UpdateCodeGenBusinessParam


class CodeGenBusinessService:
    """Code generation business service class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> CodeGenBusiness:
        """
        Get the business with the specified ID

        :param db: database session
        :param pk: business ID
        :return:
        """

        business = await code_gen_business_dao.get(db, pk)
        if not business:
            raise errors.NotFoundError(msg='Code generation business does not exist')
        return business

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[CodeGenBusiness]:
        """
        Get all business

        :param db: database session
        :return:
        """

        return await code_gen_business_dao.get_all(db)

    @staticmethod
    async def get_list(*, db: AsyncSession, table_name: str) -> dict[str, Any]:
        """
        Get a list of code generation businesses

        :param db: database session
        :param table_name: business table name
        :return:
        """
        business_select = await code_gen_business_dao.get_select(table_name=table_name)
        return await paging_data(db, business_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateCodeGenBusinessParam) -> None:
        """
        Create a business

        :param db: database session
        :param obj: Create business parameters
        :return:
        """

        business = await code_gen_business_dao.get_by_name(db, obj.table_name)
        if business:
            raise errors.ConflictError(msg='Code generation business already exists')
        await code_gen_business_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateCodeGenBusinessParam) -> int:
        """
        Update business

        :param db: database session
        :param pk: business ID
        :param obj: Update business parameters
        :return:
        """

        business = await code_gen_business_dao.get(db, pk)
        if not business:
            raise errors.NotFoundError(msg='Code generation business does not exist')
        if business.table_name != obj.table_name and await code_gen_business_dao.get_by_name(db, obj.table_name):
            raise errors.ConflictError(msg='Code generation business already exists')
        return await code_gen_business_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        Delete business

        :param db: database session
        :param pk: business ID
        :return:
        """

        business = await code_gen_business_dao.get(db, pk)
        if not business:
            raise errors.NotFoundError(msg='Code generation business does not exist')
        return await code_gen_business_dao.delete(db, pk)


code_gen_business_service: CodeGenBusinessService = CodeGenBusinessService()
