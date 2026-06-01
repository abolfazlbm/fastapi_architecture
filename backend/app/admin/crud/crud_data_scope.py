from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, and_, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig

from backend.app.admin.model import DataRule, DataScope, data_scope_rule
from backend.app.admin.schema.data_scope import (
    CreateDataScopeParam,
    CreateDataScopeRuleParam,
    UpdateDataScopeParam,
    UpdateDataScopeRuleParam,
)
from backend.utils.serializers import select_join_serialize
from backend.utils.timezone import timezone


class CRUDDataScope(CRUDPlus[DataScope]):
    """Data scope database operation class"""

    async def get(self, db: AsyncSession, pk: int) -> DataScope | None:
        """
        Get data range details

        :param db: database session
        :param pk: Range ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_by_name(self, db: AsyncSession, name: str) -> DataScope | None:
        """
        Get data range by name

        :param db: database session
        :param name: range name
        :return:
        """
        return await self.select_model_by_column(db, name=name, deleted=0)

    async def get_join(self, db: AsyncSession, pk: int) -> Any:
        """
        Get data range associated data

        :param db: database session
        :param pk: Range ID
        :return:
        """
        result = await self.select_models(
            db,
            id=pk,
            deleted=0,
            join_conditions=[
                JoinConfig(model=data_scope_rule, join_on=data_scope_rule.c.data_scope_id == self.model.id),
                JoinConfig(
                    model=DataRule,
                    join_on=and_(DataRule.id == data_scope_rule.c.data_rule_id, DataRule.deleted == 0),
                    fill_result=True,
                ),
            ],
        )

        return select_join_serialize(result, relationships=['DataScope-m2m-DataRule:rules'])

    async def get_all(self, db: AsyncSession) -> Sequence[DataScope]:
        """
        Get all data ranges

        :param db: database session
        :return:
        """
        return await self.select_models(db, deleted=0)

    async def get_all_by_ids(self, db: AsyncSession, pks: list[int]) -> Sequence[DataScope]:
        """
        通过 ID 列表批量获取数据范围

        :param db: 数据库会话
        :param pks: 范围 ID 列表
        :return:
        """
        return await self.select_models(db, id__in=pks, deleted=0)

    async def get_select(self, name: str | None, status: int | None) -> Select:
        """
        Get data range list query expression

        :param name: range name
        :param status: range status
        :return:
        """
        filters = {'deleted': 0}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if status is not None:
            filters['status'] = status

        return await self.select_order('id', **filters)

    async def create(self, db: AsyncSession, obj: CreateDataScopeParam) -> None:
        """
        Create data range

        :param db: database session
        :param obj: Create data range parameters
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateDataScopeParam) -> int:
        """
        Update data range

        :param db: database session
        :param pk: Range ID
        :param obj: Update data range parameters
        :return:
        """
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

    @staticmethod
    async def update_rules(db: AsyncSession, pk: int, rule_ids: UpdateDataScopeRuleParam) -> int:
        """
        Update data scope rules

        :param db: database session
        :param pk: Range ID
        :param rule_ids: Data rule ID list
        :return:
        """
        data_scope_rule_stmt = delete(data_scope_rule).where(data_scope_rule.c.data_scope_id == pk)
        await db.execute(data_scope_rule_stmt)

        if rule_ids.rules:
            data_scope_rule_data = [
                CreateDataScopeRuleParam(data_scope_id=pk, data_rule_id=rule_id).model_dump()
                for rule_id in rule_ids.rules
            ]
            data_scope_rule_stmt = insert(data_scope_rule)
            await db.execute(data_scope_rule_stmt, data_scope_rule_data)

        return len(rule_ids.rules)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        Batch delete data range

        :param db: database session
        :param pks: Range ID List
        :return:
        """
        return await self.delete_model_by_column(
            db,
            allow_multiple=True,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id__in=pks,
            deleted=0,
        )


data_scope_dao: CRUDDataScope = CRUDDataScope(DataScope)
