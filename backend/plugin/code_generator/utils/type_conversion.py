from functools import lru_cache

from backend.core.conf import settings
from backend.plugin.code_generator.enums import GenMySQLColumnType, GenPostgreSQLColumnType


@lru_cache(maxsize=128)
def sql_type_to_sqlalchemy(typing: str) -> str:
    """
    Convert SQL types to SQLAlchemy types

    :param typing: SQL type string
    :return:
    """
    if settings.DATABASE_TYPE == 'mysql':
        if typing in GenMySQLColumnType.get_member_keys():
            return typing
    else:
        if typing in GenPostgreSQLColumnType.get_member_keys():
            return typing
    return 'String'


@lru_cache(maxsize=128)
def sql_type_to_pydantic(typing: str) -> str:
    """
    Convert SQL types to Pydantic types

    :param typing: SQL type string
    :return:
    """
    try:
        if settings.DATABASE_TYPE == 'mysql':
            return GenMySQLColumnType[typing].value
        if typing == 'CHARACTER VARYING':  # postgresql 中 DDL VARCHAR 的别名
            return 'str'
        return GenPostgreSQLColumnType[typing].value
    except KeyError:
        return 'str'
