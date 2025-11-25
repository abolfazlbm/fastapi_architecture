from pydantic import Field

from backend.common.schema import SchemaBase


class GetCaptchaDetail(SchemaBase):
    """Verification code details"""

    is_enabled: bool = Field(description='Whether to enable')
    expire_seconds: int = Field(description='Expiration seconds')
    uuid: str = Field(description='Image unique identifier')
    image: str = Field(description='Image content')
