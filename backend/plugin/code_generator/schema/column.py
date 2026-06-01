from pydantic import ConfigDict, Field, field_validator

from backend.common.schema import SchemaBase
from backend.plugin.code_generator.utils.type_conversion import sql_type_to_sqlalchemy


class GenColumnSchemaBase(SchemaBase):
    """Code generation model basic model"""

    name: str = Field(description='column name')
    comment: str | None = Field(None, description='column description')
    type: str = Field(description='SQLA model column type')
    default: str | None = Field(None, description='Column default value')
    sort: int = Field(description='Column sort')
    length: int = Field(description='column length')
    is_pk: bool = Field(False, description='Is it the primary key')
    is_nullable: bool = Field(False, description='Can it be null')
    gen_business_id: int = Field(description='Code generation business ID')

    @field_validator('type')
    @classmethod
    def normalize_type(cls, v: str) -> str:
        """Normalized Type"""
        return sql_type_to_sqlalchemy(v)


class CreateGenColumnParam(GenColumnSchemaBase):
    """Create code generation model column parameters"""


class CreateGenColumnInternalParam(CreateGenColumnParam):
    """创建代码生成模型列内部参数"""

    pd_type: str | None = Field(None, description='列类型对应的 pydantic 类型')


class UpdateGenColumnParam(GenColumnSchemaBase):
    """Update code generation model column parameters"""


class GetGenColumnDetail(GenColumnSchemaBase):
    """Get code generation model column details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='primary key ID')
    pd_type: str = Field(description='The pydantic type corresponding to the column type')
