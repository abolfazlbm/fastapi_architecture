from datetime import datetime

from pydantic import ConfigDict, Field, field_validator

from backend.common.exception import errors
from backend.common.schema import SchemaBase
from backend.utils.pattern_validate import is_english_identifier


class GenBusinessSchemaBase(SchemaBase):
    """Code generation business basic model"""

    app_name: str = Field(description='Application name (English)')
    table_name: str = Field(description='Table name (English)')
    doc_comment: str = Field(description='Documentation comments (for function/parameter documentation)')
    table_comment: str | None = Field(None, description='Table description')
    class_name: str | None = Field(None, description='Used for python code base class names')
    schema_name: str | None = Field(None, description='Used for python Schema code base class names')
    filename: str | None = Field(None, description='Used for python code base filenames')
    datetime_mixin: bool = Field(True, description='Whether to include the time Mixin column')
    api_version: str = Field('v1', description='Code Generation Api Version')
    tag: str | None = Field(None, description='API label used for routing packets')
    gen_path: str | None = Field(None, description='Code Generation Path')
    remark: str | None = Field(None, description='Remark')

    @field_validator('app_name', 'table_name')
    @classmethod
    def validate_english_only(cls, v: str) -> str:
        """Validate English fields"""
        if not is_english_identifier(v):
            raise errors.RequestError(msg='Must start with an English letter and contain only English letters and underscores')
        return v


class CreateGenBusinessParam(GenBusinessSchemaBase):
    """Create code to generate business parameters"""


class UpdateGenBusinessParam(GenBusinessSchemaBase):
    """Update code generation business parameters"""


class GetGenBusinessDetail(GenBusinessSchemaBase):
    """Get code generation business details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Primary key ID')
    created_time: datetime = Field(description='Creation time')
    updated_time: datetime | None = Field(None, description='Update time')
