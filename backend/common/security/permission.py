from typing import Any

from fastapi import Request
from sqlalchemy import Alias, ColumnElement, Table, and_, or_
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy_crud_plus.types import Model

from backend.common.context import ctx
from backend.common.enums import RoleDataRuleExpressionType, RoleDataRuleOperatorType
from backend.common.exception import errors
from backend.core.conf import settings
from backend.utils.dynamic_import import get_all_models


class RequestPermission:
    """
    Request permission validator for role menu RBAC permission control

    Notice:
        When using this request permission, you need to set `Depends(RequestPermission('xxx'))` before `DependsRBAC`,
        Because the interface dependency injection of the current version of FastAPI is performed in positive order, it means that the RBAC identity will be set before verification
    """

    def __init__(self, value: str) -> None:
        """
        Initialize the request permission validator

        :param value: permission identifier
        :return:
        """
        self.value = value

    async def __call__(self, request: Request) -> None:
        """
        Verify request permissions

        :param request: FastAPI request object
        :return:
        """
        if settings.RBAC_ROLE_MENU_MODE:
            if not isinstance(self.value, str):
                raise errors.ServerError
            # Attach permissions to identify the request status
            ctx.permission = self.value


def get_data_permission_models() -> dict[str, object]:
    """Get all models available for data permissions"""
    return {getattr(model, '__name__', str(model)): model for model in get_all_models()}


def filter_data_permission(  # noqa: C901
    request: Request, *models: type[Model] | AliasedClass | Alias | Table
) -> ColumnElement[bool]:
    """
    Filter data permissions to control the user's visible data range

    Use scenarios:
        - Control what data users can see

    :param request: FastAPI request object
    :param models: model classes that require application data permissions
    :return:
    """
    #Super administrator does not filter
    if request.user.is_superuser:
        return or_(1 == 1)

    # Role does not have data permission filtering enabled
    for role in request.user.roles:
        if not role.is_filter_scopes:
            return or_(1 == 1)

    # Get data rules
    data_rules = set()
    for role in request.user.roles:
        for scope in role.scopes:
            if scope.status:
                data_rules.update(scope.rules)

    if not data_rules:
        return or_(1 == 1)

    # GetTargetModel
    model_map = (
        {getattr(model, '__name__', str(model)): model for model in models} if models else get_data_permission_models()
    )

    where_and_list = []
    where_or_list = []

    for data_rule in data_rules:
        target_model = model_map.get(data_rule.model)
        if target_model is None:
            continue

        table = target_model if isinstance(target_model, Table) else target_model.__table__
        rule_column = data_rule.column
        if rule_column not in table.columns.keys():
            continue
        if rule_column in settings.DATA_PERMISSION_COLUMN_EXCLUDE:
            continue

        # Create filter conditions
        column_obj = (
            getattr(target_model, rule_column) if not isinstance(target_model, Table) else table.columns[rule_column]
        )
        column_type = table.columns[rule_column].type.python_type

        def cast_value(value: Any) -> Any:
            """Type Conversion"""
            try:
                return column_type(value) if column_type is not str else value
            except (ValueError, TypeError):
                return value
        condition = None
        match data_rule.expression:
            case RoleDataRuleExpressionType.eq:
                condition = column_obj == cast_value(data_rule.value)
            case RoleDataRuleExpressionType.ne:
                condition = column_obj != cast_value(data_rule.value)
            case RoleDataRuleExpressionType.gt:
                condition = column_obj > cast_value(data_rule.value)
            case RoleDataRuleExpressionType.ge:
                condition = column_obj >= cast_value(data_rule.value)
            case RoleDataRuleExpressionType.lt:
                condition = column_obj < cast_value(data_rule.value)
            case RoleDataRuleExpressionType.le:
                condition = column_obj <= cast_value(data_rule.value)
            case RoleDataRuleExpressionType.in_:
                values = [cast_value(v.strip()) for v in data_rule.value.split(',')]
                condition = column_obj.in_(values)
            case RoleDataRuleExpressionType.not_in:
                values = [cast_value(v.strip()) for v in data_rule.value.split(',')]
                condition = column_obj.not_in(values)

        # Add to the corresponding list according to the operator
        if condition is not None:
            match data_rule.operator:
                case RoleDataRuleOperatorType.AND:
                    where_and_list.append(condition)
                case RoleDataRuleOperatorType.OR:
                    where_or_list.append(condition)

    # Combining all conditions
    where_list = []
    if where_and_list:
        where_list.append(and_(*where_and_list))
    if where_or_list:
        where_list.append(or_(*where_or_list))

    return or_(*where_list) if where_list else or_(1 == 1)


# This function is to simplify the calling method, but it currently does not work properly: https://github.com/fastapi/fastapi/discussions/14438
# def DataPermissionFilter(*models: type[Model] | AliasedClass | Alias | Table) -> type[ColumnElement[bool]]:
#     """
#     Specify the data permission filter for the model
#
#     :param models: model class (optional, multiple supported)
#     :return:
#     """
#     return Annotated[ColumnElement[bool], Depends(partial(filter_data_permission, *models))]


class DataPermissionFilter:
    """Specify data permission filters for models"""

    def __init__(self, *models: type[Model] | AliasedClass | Alias | Table) -> None:
        self.models = models

    async def __call__(self, request: Request) -> ColumnElement[bool]:
        return filter_data_permission(request, *self.models)
