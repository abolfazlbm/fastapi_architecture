from backend.common.enums import StrEnum


class UserSocialType(StrEnum):
    """User social type"""

    github = 'Github'
    google = 'Google'
    linux_do = 'LinuxDo'


class UserSocialAuthType(StrEnum):
    """User social authorization type"""

    login = 'login'
    binding = 'binding'
