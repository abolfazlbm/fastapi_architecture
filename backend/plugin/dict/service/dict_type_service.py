from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.dict.crud.crud_dict_type import dict_type_dao
from backend.plugin.dict.model import DictType
from backend.plugin.dict.schema.dict_type import CreateDictTypeParam, DeleteDictTypeParam, UpdateDictTypeParam


class DictTypeService:
    """Dictionary type service class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> DictType:
        """
        Get dictionary type details

        :param db: database session
        :param pk: dictionary type ID
        :return:
        """

        dict_type = await dict_type_dao.get(db, pk)
        if not dict_type:
            raise errors.NotFoundError(msg='Dictionary type does not exist')
        return dict_type

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[DictType]:
        """
        Get all dictionary types

        :param db: database session
        :return:
        """
        dict_datas = await dict_type_dao.get_all(db)
        return dict_datas

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None, code: str | None) -> dict[str, Any]:
        """
        Get a list of dictionary types

        :param db: database session
        :param name: dictionary type name
        :param code: dictionary type encoding
        :return:
        """
        dict_type_select = await dict_type_dao.get_select(name=name, code=code)
        return await paging_data(db, dict_type_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDictTypeParam) -> None:
        """
        Create dictionary type

        :param db: database session
        :param obj: dictionary type creation parameter
        :return:
        """

        dict_type = await dict_type_dao.get_by_code(db, obj.code)
        if dict_type:
            raise errors.ConflictError(msg='Dictionary type already exists')
        await dict_type_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDictTypeParam) -> int:
        """
        Update dictionary type

        :param db: database session
        :param pk: dictionary type ID
        :param obj: dictionary type update parameter
        :return:
        """

        dict_type = await dict_type_dao.get(db, pk)
        if not dict_type:
            raise errors.NotFoundError(msg='Dictionary type does not exist')
        if dict_type.code != obj.code and await dict_type_dao.get_by_code(db, obj.code):
            raise errors.ConflictError(msg='Dictionary type already exists')
        count = await dict_type_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteDictTypeParam) -> int:
        """
        Delete dictionary types in batches

        :param db: database session
        :param obj: dictionary type ID list
        :return:
        """

        count = await dict_type_dao.delete(db, obj.pks)
        return count


dict_type_service: DictTypeService = DictTypeService()
