from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.cache.decorator import cache_invalidate, cached
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.plugin.dict.crud.crud_dict_data import dict_data_dao
from backend.plugin.dict.crud.crud_dict_type import dict_type_dao
from backend.plugin.dict.model import DictData
from backend.plugin.dict.schema.dict_data import CreateDictDataParam, DeleteDictDataParam, UpdateDictDataParam


class DictDataService:
    """Dictionary data service class"""

    @staticmethod
    @cached(settings.CACHE_DICT_REDIS_PREFIX, key='pk')
    async def get(*, db: AsyncSession, pk: int) -> DictData:
        """
        Get dictionary data details

        :param db: database session
        :param pk: dictionary data ID
        :return:
        """
        dict_data = await dict_data_dao.get(db, pk)
        if not dict_data:
            raise errors.NotFoundError(msg='Dictionary data does not exist')
        return dict_data

    @staticmethod
    @cached(
        settings.CACHE_DICT_REDIS_PREFIX,
        key_builder=lambda *, db, code: f'type:{code}',
    )
    async def get_by_type_code(*, db: AsyncSession, code: str) -> Sequence[DictData]:
        """
        Get dictionary data details

        :param db: database session
        :param code: dictionary type encoding
        :return:
        """
        dict_datas = await dict_data_dao.get_by_type_code(db, code)
        if not dict_datas:
            raise errors.NotFoundError(msg='Dictionary data does not exist')
        return dict_datas

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[DictData]:
        """
        Get all dictionary data

        :param db: database session
        :return:
        """
        dict_datas = await dict_data_dao.get_all(db)
        return dict_datas

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        type_code: str | None,
        label: str | None,
        value: str | None,
        status: int | None,
        type_id: int | None,
    ) -> dict[str, Any]:
        """
        Get dictionary data list

        :param db: database session
        :param type_code: dictionary type encoding
        :param label: dictionary data label
        :param value: dictionary data key value
        :param status: status
        :param type_id: dictionary type ID
        :return:
        """
        dict_data_select = await dict_data_dao.get_select(
            type_code=type_code,
            label=label,
            value=value,
            status=status,
            type_id=type_id,
        )
        return await paging_data(db, dict_data_select)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDictDataParam) -> None:
        """
        Create dictionary data

        :param db: database session
        :param obj: Dictionary data creation parameters
        :return:
        """
        dict_type = await dict_type_dao.get(db, obj.type_id)
        if not dict_type:
            raise errors.NotFoundError(msg='Dictionary type does not exist')
        dict_data = await dict_data_dao.get_by_label_and_type_code(db, obj.label, dict_type.code)
        if dict_data:
            raise errors.ConflictError(msg='Dictionary data already exists')
        await dict_data_dao.create(db, obj, dict_type.code)

    @staticmethod
    @cache_invalidate(settings.CACHE_DICT_REDIS_PREFIX)
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDictDataParam) -> int:
        """
        Update dictionary data

        :param db: database session
        :param pk: dictionary data ID
        :param obj: Dictionary data update parameter
        :return:
        """
        dict_data = await dict_data_dao.get(db, pk)
        if not dict_data:
            raise errors.NotFoundError(msg='Dictionary data does not exist')
        dict_type = await dict_type_dao.get(db, obj.type_id)
        if not dict_type:
            raise errors.NotFoundError(msg='Dictionary type does not exist')
        if dict_data.label != obj.label and await dict_data_dao.get_by_label_and_type_code(
            db, obj.label, dict_type.code
        ):
            raise errors.ConflictError(msg='Dictionary data already exists')
        count = await dict_data_dao.update(db, pk, obj, dict_type.code)
        return count

    @staticmethod
    @cache_invalidate(settings.CACHE_DICT_REDIS_PREFIX)
    async def delete(*, db: AsyncSession, obj: DeleteDictDataParam) -> int:
        """
        Delete dictionary data in batches

        :param db: database session
        :param obj: Dictionary data ID list
        :return:
        """
        count = await dict_data_dao.delete(db, obj.pks)
        return count


dict_data_service: DictDataService = DictDataService()
