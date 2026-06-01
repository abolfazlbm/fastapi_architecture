from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, Field, field_validator

from backend.common.enums import PluginLevelType
from backend.core.path_conf import PLUGIN_DIR
from backend.plugin.errors import PluginConfigError
from backend.utils.pattern_validate import match_string

# Supported tag types
_VALID_TAGS: Final = frozenset({'ai', 'mcp', 'agent', 'auth', 'storage', 'notification', 'task', 'payment', 'other'})

# Supported database types
_VALID_DATABASES: Final = frozenset({'mysql', 'postgresql'})


class PluginInfoSchema(BaseModel):
    """Plugin information model"""

    icon: str | None = Field(default=None, description='icon path or link address')
    summary: str = Field(..., min_length=1, max_length=100, description='summary')
    version: str = Field(..., description='Version number')
    description: str = Field(..., min_length=1, max_length=500, description='description')
    author: str = Field(..., min_length=1, max_length=50, description='author')
    tags: list[str] = Field(..., min_length=1, description='tag')
    database: list[str] = Field(..., min_length=1, description='Database support')
    depends_on: list[str] = Field(default_factory=list, description='依赖的插件列表')

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Verify the version number format"""
        if not match_string(r'^\d+\.\d+\.\d+$', v):
            raise PluginConfigError(f'The version number is in the wrong format, it should be in x.y.z format, such as 1.0.0, the current value: {v}')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Verify the label"""
        if v:
            invalid_tags = set(v) - _VALID_TAGS
            if invalid_tags:
                raise PluginConfigError(
                    f'The tag value is invalid: {", ".join(invalid_tags)}，Supported tags: {", "
                                                                                         "".join(sorted(_VALID_TAGS))}'
                )
        return v

    @field_validator('database')
    @classmethod
    def validate_database(cls, v: list[str]) -> list[str]:
        """Verify the database type"""
        if v:
            invalid_dbs = set(v) - _VALID_DATABASES
            if invalid_dbs:
                raise PluginConfigError(
                    f'The database type is invalid: {", ".join(invalid_dbs)}，Supported databases: {", ".join(sorted(_VALID_DATABASES))}'
                )
        return v

    @field_validator('depends_on')
    @classmethod
    def validate_depends_on(cls, v: list[str]) -> list[str]:
        """校验插件依赖配置"""
        for dep in v:
            if not dep or not isinstance(dep, str):
                raise PluginConfigError(f'依赖的插件列表必须为非空字符串，当前值: {dep}')
        return v


class AppPluginAppSchema(BaseModel):
    """App-level plug-in app configuration model"""

    router: list[str] = Field(..., min_length=1, description='List of router instances')

    @field_validator('router')
    @classmethod
    def validate_router(cls, v: list[str]) -> list[str]:
        """Verify the router configuration"""
        if not v:
            raise PluginConfigError('router The configuration cannot be empty')
        for router in v:
            if not router or not isinstance(router, str):
                raise PluginConfigError(f'router The configuration item must be a non-empty string, the current value: {router}')
        return v


class ExtendPluginAppSchema(BaseModel):
    """Extension-level plug-in app configuration model"""

    extend: str = Field(..., min_length=1, description='The name of the app folder for the extension')


class ApiConfigSchema(BaseModel):
    """API Configure the model"""

    prefix: str = Field(..., min_length=1, description='Routing prefix')
    tags: str = Field(..., min_length=1, description='Swagger Document labels')

    @field_validator('prefix')
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Validate route prefixes"""
        if not v.startswith('/'):
            raise PluginConfigError(f'The route prefix must start with "/", the current value: {v}')
        if not match_string(r'^/[a-zA-Z0-9_/-]*$', v):
            raise PluginConfigError(f'The route prefix is malformed and can only contain letters, numbers, underscores, slashes, and hyphens, with current values: {v}')
        return v


class AppPluginConfigSchema(BaseModel):
    """Application-level plug-in configuration model"""

    plugin: PluginInfoSchema = Field(..., description='Plugin information')
    app: AppPluginAppSchema = Field(..., description='App configuration')
    settings: dict[str, Any] = Field(default_factory=dict, description='Configure items')

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v: dict[str, Any]) -> dict[str, Any]:
        """The name of the validation configuration item must be capitalized"""
        if v:
            invalid_keys = [key for key in v if not key.isupper()]
            if invalid_keys:
                raise PluginConfigError(f'settings The configuration item name must be capitalized, and the configuration item is invalid: {", ".join(invalid_keys)}')
        return v


class ExtendPluginConfigSchema(BaseModel):
    """Extension-level plug-in configuration model"""

    plugin: PluginInfoSchema = Field(..., description='Plugin information')
    app: ExtendPluginAppSchema = Field(..., description='App configuration')
    api: dict[str, ApiConfigSchema] = Field(..., min_length=1, description='Interface configuration')
    settings: dict[str, Any] = Field(default_factory=dict, description='Configure items')

    @field_validator('api', mode='before')
    @classmethod
    def validate_api_config(cls, v: dict[str, Any]) -> dict[str, ApiConfigSchema]:
        """Validate and transform API configurations"""
        if not v:
            raise PluginConfigError('Extension-level plugins must contain at least one API configuration')
        validated_api = {}
        for api_name, api_config in v.items():
            if not api_name or not isinstance(api_name, str):
                raise PluginConfigError(f'api The configuration name must be a non-empty string, the current value: {api_name}')
            if not match_string(r'^[a-zA-Z_][a-zA-Z0-9_]*$', api_name):
                raise PluginConfigError(
                    f'api The configuration name is malformed, must start with a letter or underscore, and can only contain letters, numbers, and underscores, the current value: {api_name}'
                )
            validated_api[api_name] = ApiConfigSchema(**api_config) if isinstance(api_config, dict) else api_config
        return validated_api

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v: dict[str, Any]) -> dict[str, Any]:
        """The name of the validation configuration item must be capitalized"""
        if v:
            invalid_keys = [key for key in v if not key.isupper()]
            if invalid_keys:
                raise PluginConfigError(f'settings The configuration item name must be capitalized, and the configuration item is invalid: {", ".join(invalid_keys)}')
        return v


def validate_plugin_config(plugin_name: str, config: dict[str, Any]) -> PluginLevelType:
    """
    Verify the plug-in configuration

    :p aram plugin_name: Plugin name
    :p aram config: Plugin configuration dictionary
    :return:
    """
    is_extend_plugin = 'api' in config

    try:
        if is_extend_plugin:
            ExtendPluginConfigSchema.model_validate(config)
            plugin_level = PluginLevelType.extend
        else:
            AppPluginConfigSchema.model_validate(config)
            plugin_level = PluginLevelType.app
    except Exception as e:
        error_msg = str(e)
        # Format the Pydantic error message
        if hasattr(e, 'errors'):
            errors = e.errors()
            error_details = []
            for error in errors:
                loc = '.'.join(str(loc) for loc in error['loc'])
                msg = error['msg']
                error_details.append(f'{loc}: {msg}')
            error_msg = '; '.join(error_details)
        raise PluginConfigError(f'Plugin {plugin_name} configuration validation failed: {error_msg}') from e

    depends_on = config['plugin'].get('depends_on', [])
    if plugin_name in depends_on:
        raise PluginConfigError(f'PlugIn {plugin_name} cannot rely on oneself')

    plugin_dir = Path(PLUGIN_DIR) / plugin_name
    model_dir = plugin_dir / 'model'
    if model_dir.is_dir():
        sql_dir = plugin_dir / 'sql'
        supported_db_types = []
        missing_details = []

        for db_type in ('mysql', 'postgresql'):
            db_sql_dir = sql_dir / db_type
            required_sql_files = (
                db_sql_dir / 'init.sql',
                db_sql_dir / 'destroy.sql',
                db_sql_dir / 'init_snowflake.sql',
                db_sql_dir / 'destroy_snowflake.sql',
            )
            missing_files = [
                str(sql_file.relative_to(plugin_dir)) for sql_file in required_sql_files if not sql_file.is_file()
            ]

            if not missing_files:
                supported_db_types.append(db_type)
                continue

            missing_details.append(f'{db_type}: {", ".join(missing_files)}')

        if not supported_db_types:
            raise PluginConfigError(
                f'PlugIn {plugin_name} At least one database initialization and destruction SQL script must be provided,'
                f'Currently missing: {"; ".join(missing_details)}'
            )

    return plugin_level
