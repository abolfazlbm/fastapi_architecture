import anyio

from backend.common.enums import DataBaseType, PrimaryKeyType
from backend.core.path_conf import PLUGIN_DIR


def build_sql_filename(
    prefix: str,
    pk_type: PrimaryKeyType,
    *,
    suffix: str | None = None,
) -> str:
    """
    Build a plugin SQL script filename

    :param prefix: SQL script filename prefix, such as init or destroy
    :param pk_type: Primary-key type; snowflake ID mode appends the snowflake marker
    :param suffix: Optional filename suffix appended after the primary-key type marker
    :return:
    """
    parts = [prefix]
    if pk_type == PrimaryKeyType.snowflake:
        parts.append('snowflake')
    if suffix:
        parts.append(suffix)
    return f'{"_".join(parts)}.sql'


async def get_plugin_sql(plugin: str, db_type: DataBaseType, pk_type: PrimaryKeyType) -> str | None:
    """
    Get a plugin SQL script

    :param plugin: Plugin Name
    :param db_type: database type
    :param pk_type: Primary key type
    :return:
    """
    sql_dir = PLUGIN_DIR / plugin / 'sql' / ('mysql' if db_type == DataBaseType.mysql else 'postgresql')
    default_filename = build_sql_filename('init', pk_type)
    default_sql_file = sql_dir / default_filename
    return str(default_sql_file) if await anyio.Path(default_sql_file).exists() else None


async def get_plugin_destroy_sql(plugin: str, db_type: DataBaseType, pk_type: PrimaryKeyType) -> str | None:
    """
    Get a plugin destroy SQL script

    :param plugin: Plugin Name
    :param db_type: database type
    :param pk_type: Primary key type
    :return:
    """
    sql_dir = PLUGIN_DIR / plugin / 'sql' / ('mysql' if db_type == DataBaseType.mysql else 'postgresql')
    sql_file = sql_dir / build_sql_filename('destroy', pk_type)
    return str(sql_file) if await anyio.Path(sql_file).exists() else None
