from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.conf import settings
from backend.plugin.core import check_plugin_installed
from backend.utils.serializers import select_list_serialize


def _to_bool(value: str) -> bool:
    """Convert string to boolean"""
    return value == 'true'


async def _load_config(
    db: AsyncSession,
    config_type_attr: str,
    mapping: dict[str, Callable[[str], object]],
    status_key: str,
) -> None:
    """
    Load configuration based on configuration type

    :param db: database session
    :param config_type_attr: Configuration type attribute name
    :param mapping: configuration mapping {config_key: converter}
    :param status_key: status key
    :return:
    """
    if not check_plugin_installed('config'):
        return

    try:
        from backend.plugin.config.enums import ConfigType
        from backend.plugin.config.service.config_service import config_service
    except ImportError as e:
        raise ImportError('Parameter configuration plug-in usage failed to import, please contact the system administrator') from e

    config_type = getattr(ConfigType, config_type_attr)
    dynamic_config = await config_service.get_all(db=db, type=config_type)
    if not dynamic_config:
        return

    config_list = select_list_serialize(dynamic_config) if hasattr(dynamic_config[0], '__table__') else dynamic_config
    configs = {dc['key']: dc['value'] for dc in config_list}
    if configs.get(status_key, '1') == '0':
        return

    for config_key, converter in mapping.items():
        if config_key in configs:
            setattr(settings, config_key, converter(configs[config_key]))


async def load_user_security_config(db: AsyncSession) -> None:
    """
    Get user security configuration

    :param db: database session
    :return:
    """
    mapping = {
        'USER_LOCK_THRESHOLD': int,
        'USER_LOCK_SECONDS': int,
        'USER_PASSWORD_EXPIRY_DAYS': int,
        'USER_PASSWORD_REMINDER_DAYS': int,
        'USER_PASSWORD_HISTORY_CHECK_COUNT': int,
        'USER_PASSWORD_MIN_LENGTH': int,
        'USER_PASSWORD_MAX_LENGTH': int,
        'USER_PASSWORD_REQUIRE_SPECIAL_CHAR': _to_bool,
    }
    await _load_config(db, 'user_security', mapping, 'USER_SECURITY_CONFIG_STATUS')


async def load_login_config(db: AsyncSession) -> None:
    """
    Get login configuration

    :param db: database session
    :return:
    """
    mapping = {
        'LOGIN_CAPTCHA_ENABLED': _to_bool,
    }
    await _load_config(db, 'login', mapping, 'LOGIN_CONFIG_STATUS')


async def load_email_config(db: AsyncSession) -> None:
    """
    Get email configuration

    :param db: database session
    :return:
    """
    mapping = {
        'EMAIL_HOST': str,
        'EMAIL_PORT': int,
        'EMAIL_SSL': _to_bool,
        'EMAIL_USERNAME': str,
        'EMAIL_PASSWORD': str,
    }
    await _load_config(db, 'email', mapping, 'EMAIL_CONFIG_STATUS')
