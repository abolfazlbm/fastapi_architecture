from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class ConfigSchemaBase(SchemaBase):
    """Parameter configuration basic model"""

    name: str = Field(description='Parameter configuration name')
    type: str | None = Field(None, description='Parameter configuration type')
    key: str = Field(description='Parameter configuration key name')
    value: str = Field(description='Parameter configuration value')
    is_frontend: bool = Field(description='Whether the front-end parameters are configured')
    remark: str | None = Field(None, description='Remarks')


class CreateConfigParam(ConfigSchemaBase):
    """Create parameter configuration parameters"""


class UpdateConfigParam(ConfigSchemaBase):
    """Update parameter configuration parameters"""


class UpdateConfigsParam(UpdateConfigParam):
    """Batch update parameter configuration parameters"""

    id: int = Field(description='Parameter configuration ID')


class GetConfigDetail(ConfigSchemaBase):
    """Parameter configuration details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Parameter configuration ID')
    created_time: datetime = Field(description='Creation time')
    updated_time: datetime | None = Field(None, description='Update time')
