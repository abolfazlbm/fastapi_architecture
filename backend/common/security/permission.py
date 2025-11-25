from fastapi import Request
from sqlalchemy import ColumnElement, and_, or_

from backend.app.admin.schema.user import GetUserInfoWithRelationDetail
from backend.common.context import ctx
from backend.common.enums import RoleDataRuleExpressionType, RoleDataRuleOperatorType
from backend.common.exception import errors
from backend.core.conf import settings
from backend.utils.import_parse import dynamic_import_data_model


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


def filter_data_permission(request_user: GetUserInfoWithRelationDetail) -> ColumnElement[bool]:  # noqa: C901
    """
    Filter data permissions to control the user's visible data range

    Use scenarios:
        - Control what data users can see

    :param request_user: request user
    :return:
    """
    # Whether to filter data permissions
    if request_user.is_superuser:
        return or_(1 == 1)

    for role in request_user.roles:
        if not role.is_filter_scopes:
            return or_(1 == 1)

    # Get data rules
    data_rules = set()
    for role in request_user.roles:
        for scope in role.scopes:
            if scope.status:
                data_rules.update(scope.rules)

    # No rules for users not to filter
    if not list(data_rules):
        return or_(1 == 1)

    where_and_list = []
    where_or_list = []

    for data_rule in list(data_rules):
        # Verification rule model
        rule_model = data_rule.model
        if rule_model not in settings.DATA_PERMISSION_MODELS:
            raise errors.NotFoundError(msg='The available model for data rules does not exist')
        model_ins = dynamic_import_data_model(settings.DATA_PERMISSION_MODELS[rule_model])

        # Verify rule column
        model_columns = [
            key for key in model_ins.__table__.columns.keys() if key not in settings.DATA_PERMISSION_COLUMN_EXCLUDE
        ]
        column = data_rule.column
        if column not in model_columns:
            raise errors.NotFoundError(msg='The available model column for the data rule does not exist')

        # Create filter conditions
        column_obj = getattr(model_ins, column)
        rule_expression = data_rule.expression
        condition = None
        match rule_expression:
            case RoleDataRuleExpressionType.eq:
                condition = column_obj == data_rule.value
            case RoleDataRuleExpressionType.ne:
                condition = column_obj != data_rule.value
            case RoleDataRuleExpressionType.gt:
                condition = column_obj > data_rule.value
            case RoleDataRuleExpressionType.ge:
                condition = column_obj >= data_rule.value
            case RoleDataRuleExpressionType.lt:
                condition = column_obj < data_rule.value
            case RoleDataRuleExpressionType.le:
                condition = column_obj <= data_rule.value
            case RoleDataRuleExpressionType.in_:
                values = data_rule.value.split(',') if isinstance(data_rule.value, str) else data_rule.value
                condition = column_obj.in_(values)
            case RoleDataRuleExpressionType.not_in:
                values = data_rule.value.split(',') if isinstance(data_rule.value, str) else data_rule.value
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
