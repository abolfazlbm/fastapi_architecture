from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase
from backend.plugin.oauth2.enums import UserSocialType


class UserSocialSchemaBase(SchemaBase):
    """User social basic model"""

    sid: str = Field(description='Third-party User ID')
    source: UserSocialType = Field(description='social platform')


class CreateUserSocialParam(UserSocialSchemaBase):
    """Create user social parameters"""

    user_id: int = Field(description='User ID')


class UpdateUserSocialParam(SchemaBase):
    """Update user social parameters"""


class GetUserSocialDetail(CreateUserSocialParam):
    """Get user social details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='User social ID')
