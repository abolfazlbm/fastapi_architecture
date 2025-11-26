from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.crud.crud_data_rule import data_rule_dao
from backend.app.admin.model import DataRule
from backend.app.admin.schema.data_rule import (
    CreateDataRuleParam,
    DeleteDataRuleParam,
    GetDataRuleColumnDetail,
    UpdateDataRuleParam,
)
from backend.app.admin.utils.cache import user_cache_manager
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.utils.import_parse import dynamic_import_data_model


class DataRuleService:
    """Data Rules Service Class"""

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> DataRule:
        """
        Get data rules details

        :param db: database session
        :param pk: Rule ID
        :return:
        """

        data_rule = await data_rule_dao.get(db, pk)
        if not data_rule:
            raise errors.NotFoundError(msg='Data rule does not exist')
        return data_rule

    @staticmethod
    async def get_models() -> list[str]:
        """Get all data rules available models"""
        return list(settings.DATA_PERMISSION_MODELS.keys())

    @staticmethod
    async def get_columns(model: str) -> list[GetDataRuleColumnDetail]:
        """
        Get a list of fields for available models for data rules

        :param model: model name
        :return:
        """
        if model not in settings.DATA_PERMISSION_MODELS:
            raise errors.NotFoundError(msg='The available model of data rules does not exist')
        model_ins = dynamic_import_data_model(settings.DATA_PERMISSION_MODELS[model])

        model_columns = [
            GetDataRuleColumnDetail(key=column.key, comment=column.comment)
            for column in model_ins.__table__.columns
            if column.key not in settings.DATA_PERMISSION_COLUMN_EXCLUDE
        ]
        return model_columns

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None) -> dict[str, Any]:
        """
        Get a list of data rules

        :param db: database session
        :param name: rule name
        :return:
        """
        data_rule_select = await data_rule_dao.get_select(name=name)
        return await paging_data(db, data_rule_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[DataRule]:
        """
        Get all data rules

        :param db: database session
        :return:
        """

        data_rules = await data_rule_dao.get_all(db)
        return data_rules

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateDataRuleParam) -> None:
        """
        Create data rules

        :param db: database session
        :param obj: Rule creation parameters
        :return:
        """
        data_rule = await data_rule_dao.get_by_name(db, obj.name)
        if data_rule:
            raise errors.ConflictError(msg='Data rules already exist')
        await data_rule_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateDataRuleParam) -> int:
        """
        Update data rules

        :param db: database session
        :param pk: Rule ID
        :param obj: Rule update parameters
        :return:
        """
        data_rule = await data_rule_dao.get(db, pk)
        if not data_rule:
            raise errors.NotFoundError(msg='Data rule does not exist')
        if data_rule.name != obj.name and await data_rule_dao.get_by_name(db, obj.name):
            raise errors.ConflictError(msg='Data rule already exists')
        count = await data_rule_dao.update(db, pk, obj)
        await user_cache_manager.clear_by_data_rule_id(db, [pk])
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteDataRuleParam) -> int:
        """
        Batch deletion rules

        :param db: database session
        :param obj: Rule ID list
        :return:
        """
        count = await data_rule_dao.delete(db, obj.pks)
        await user_cache_manager.clear_by_data_rule_id(db, obj.pks)
        return count


data_rule_service: DataRuleService = DataRuleService()
