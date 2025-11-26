from pydantic import Field

from backend.common.schema import SchemaBase


class UserPasswordHistoryBase(SchemaBase):
    """Basic model of user history password recording"""

    user_id: int = Field(description='User ID')
    password: str = Field(description='Historical password')


class CreateUserPasswordHistoryParam(UserPasswordHistoryBase):
    """Create user history password records"""
