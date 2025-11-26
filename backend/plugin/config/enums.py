from backend.common.enums import StrEnum


class ConfigType(StrEnum):
    """Configuration type"""

    email = 'EMAIL'
    user_security = 'USER_SECURITY'
    login = 'LOGIN'
