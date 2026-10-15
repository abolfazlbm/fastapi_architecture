from pydantic import Field

from backend.common.schema import SchemaBase


class UserPasswordHistorySchemaBase(SchemaBase):
    """Basic model of user history password recording"""

    user_id: int = Field(description='User ID')
    password: str = Field(description='Historical password')


class CreateUserPasswordHistoryParam(UserPasswordHistorySchemaBase):
    """Create user history password records"""
