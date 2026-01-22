from pydantic import Field

from backend.common.schema import SchemaBase


class ImportParam(SchemaBase):
    """Import parameters"""

    app: str = Field(description='Application name, used to generate code to the specified app')
    table_schema: str = Field(description='Database name')
    table_name: str = Field(description='Database table name')
