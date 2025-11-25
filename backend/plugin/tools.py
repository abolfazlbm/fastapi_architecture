import json
import os
import subprocess
import sys
import warnings

from functools import lru_cache
from importlib.metadata import PackageNotFoundError, distribution
from typing import Any

import anyio
import rtoml

from fastapi import APIRouter, Depends, Request
from packaging.requirements import Requirement
from starlette.concurrency import run_in_threadpool

from backend.common.enums import DataBaseType, PrimaryKeyType, StatusType
from backend.common.exception import errors
from backend.common.log import log
from backend.core.conf import settings
from backend.core.path_conf import PLUGIN_DIR
from backend.database.redis import RedisCli, redis_client
from backend.utils._await import run_await
from backend.utils.import_parse import get_model_objects, import_module_cached


class PluginConfigError(Exception):
    """Plugin information error"""


class PluginInjectError(Exception):
    """Plugin injection error"""


class PluginInstallError(Exception):
    """Plugin installation error"""


@lru_cache
def get_plugins() -> list[str]:
    """Get the plugin list"""
    plugin_packages = []

    #Travel the plugin directory
    for item in os.listdir(PLUGIN_DIR):
        item_path = PLUGIN_DIR / item
        if not os.path.isdir(item_path) and item == '__pycache__':
            continue

        # Check whether it is a directory and contains the __init__.py file
        if os.path.isdir(item_path) and '__init__.py' in os.listdir(item_path):
            plugin_packages.append(item)

    return plugin_packages


def get_plugin_models() -> list[type]:
    """Get all model classes in the plugin"""
    objs = []

    for plugin in get_plugins():
        module_path = f'backend.plugin.{plugin}.model'
        obj = get_model_objects(module_path)
        if obj:
            objs.extend(obj)

    return objs


async def get_plugin_sql(plugin: str, db_type: DataBaseType, pk_type: PrimaryKeyType) -> str | None:
    """
    Get plugin SQL scripts

    :param plugin: plugin name
    :param db_type: database type
    :param pk_type: primary key type
    :return:
    """
    if db_type == DataBaseType.mysql:
        mysql_dir = PLUGIN_DIR / plugin / 'sql' / 'mysql'
        if pk_type == PrimaryKeyType.autoincrement:
            sql_file = mysql_dir / 'init.sql'
        else:
            sql_file = mysql_dir / 'init_snowflake.sql'
    else:
        postgresql_dir = PLUGIN_DIR / plugin / 'sql' / 'postgresql'
        if pk_type == PrimaryKeyType.autoincrement:
            sql_file = postgresql_dir / 'init.sql'
        else:
            sql_file = postgresql_dir / 'init_snowflake.sql'

    path = anyio.Path(sql_file)
    if not await path.exists():
        return None

    return sql_file


def load_plugin_config(plugin: str) -> dict[str, Any]:
    """
    Load plugin configuration

    :param plugin: Plugin Name
    :return:
    """
    toml_path = PLUGIN_DIR / plugin / 'plugin.toml'
    if not os.path.exists(toml_path):
        raise PluginInjectError(f'Plugin {plugin} is missing plugin.toml configuration file, please check if the plugin is legal')

    with open(toml_path, encoding='utf-8') as f:
        return rtoml.load(f)


def parse_plugin_config() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Resolve plug-in configuration"""

    extend_plugins = []
    app_plugins = []

    plugins = get_plugins()

    # Use independent singletons to avoid conflicts with the main thread
    current_redis_client = RedisCli()

    # Clean up unknown plug-in information
    run_await(current_redis_client.delete_prefix)(
        settings.PLUGIN_REDIS_PREFIX,
        exclude=[f'{settings.PLUGIN_REDIS_PREFIX}:{key}' for key in plugins],
    )

    for plugin in plugins:
        data = load_plugin_config(plugin)

        plugin_info = data.get('plugin')
        if not plugin_info:
            raise PluginConfigError(f'Plugin {plugin} configuration file is missing plugin configuration')

        required_fields = ['summary', 'version', 'description', 'author']
        missing_fields = [field for field in required_fields if field not in plugin_info]
        if missing_fields:
            raise PluginConfigError(f'Plugin {plugin} The configuration file is missing the required fields: {", ".join(missing_fields)}')

        if data.get('api'):
            if not data.get('app', {}).get('extend'):
                raise PluginConfigError(f'Extension-level plug-in {plugin} configuration file is missing app.extend configuration')
            extend_plugins.append(data)
        else:
            if not data.get('app', {}).get('router'):
                raise PluginConfigError(f'Application-level plugin {plugin} configuration file is missing app.router configuration')
            app_plugins.append(data)

        # Supplementary plugin information
        plugin_cache_info = run_await(current_redis_client.get)(f'{settings.PLUGIN_REDIS_PREFIX}:{plugin}')
        if plugin_cache_info:
            data['plugin']['enable'] = json.loads(plugin_cache_info)['plugin']['enable']
        else:
            data['plugin']['enable'] = str(StatusType.enable.value)
        data['plugin']['name'] = plugin

        # Cache the latest plug-in information
        run_await(current_redis_client.set)(
            f'{settings.PLUGIN_REDIS_PREFIX}:{plugin}',
            json.dumps(data, ensure_ascii=False),
        )

    # Reset plugin change status
    run_await(current_redis_client.delete)(f'{settings.PLUGIN_REDIS_PREFIX}:changed')

    # Close the connection
    run_await(current_redis_client.aclose)()

    return extend_plugins, app_plugins


def inject_extend_router(plugin: dict[str, Any]) -> None:
    """
    Extended plugin routing injection

    :param plugin: plugin name
    :return:
    """
    plugin_name: str = plugin['plugin']['name']
    plugin_api_path = PLUGIN_DIR / plugin_name / 'api'
    if not os.path.exists(plugin_api_path):
        raise PluginConfigError(f'Plugin {plugin} Missing api directory, please check if the plugin file is complete')

    for root, _, api_files in os.walk(plugin_api_path):
        for file in api_files:
            if not (file.endswith('.py') and file != '__init__.py'):
                continue

            # Parse plugin routing configuration
            file_config = plugin['api'][file[:-3]]
            prefix = file_config['prefix']
            tags = file_config['tags']

            # Get the plug-in routing module
            file_path = os.path.join(root, file)
            path_to_module_str = os.path.relpath(file_path, PLUGIN_DIR).replace(os.sep, '.')[:-3]
            module_path = f'backend.plugin.{path_to_module_str}'

            try:
                module = import_module_cached(module_path)
                plugin_router = getattr(module, 'router', None)
                if not plugin_router:
                    warnings.warn(
                        f'Extended plugin {plugin_name} module {module_path} does not have a valid router, please check if the plugin file is complete',
                        FutureWarning,
                    )
                    continue

                # Get target app route
                relative_path = os.path.relpath(root, plugin_api_path)
                app_name = plugin.get('app', {}).get('extend')
                target_module_path = f'backend.app.{app_name}.api.{relative_path.replace(os.sep, ".")}'
                target_module = import_module_cached(target_module_path)
                target_router = getattr(target_module, 'router', None)

                if not target_router or not isinstance(target_router, APIRouter):
                    raise PluginInjectError(
                        f'The extension plugin {plugin_name} module {module_path} does not have a valid router, please check if the plugin file is complete',
                    )

                # Inject plugin route into target route
                target_router.include_router(
                    router=plugin_router,
                    prefix=prefix,
                    tags=[tags] if tags else [],
                    dependencies=[Depends(PluginStatusChecker(plugin_name))],
                )
            except Exception as e:
                raise PluginInjectError(f'Extension Plugin {plugin_name} Route Injection Failed: {e!s}') from e


def inject_app_router(plugin: dict[str, Any], target_router: APIRouter) -> None:
    """
    Application-level plug-in routing injection

    :param plugin: plugin name
    :param target_router: FastAPI router
    :return:
    """
    plugin_name: str = plugin['plugin']['name']
    module_path = f'backend.plugin.{plugin_name}.api.router'
    try:
        module = import_module_cached(module_path)
        routers = plugin['app']['router']
        if not routers or not isinstance(routers, list):
            raise PluginConfigError(f'Application-level plugin {plugin_name} configuration file has an error, please check')

        for router in routers:
            plugin_router = getattr(module, router, None)
            if not plugin_router or not isinstance(plugin_router, APIRouter):
                raise PluginInjectError(
                    f'There is no valid router in the application-level plugin {plugin_name} module {module_path}, please check if the plugin file is complete',
                )

            # Inject plugin route into target route
            target_router.include_router(plugin_router, dependencies=[Depends(PluginStatusChecker(plugin_name))])
    except Exception as e:
        raise PluginInjectError(f'Application-level plugin {plugin_name} Route injection failed: {e!s}') from e


def build_final_router() -> APIRouter:
    """Build the final route"""
    extend_plugins, app_plugins = parse_plugin_config()

    for plugin in extend_plugins:
        inject_extend_router(plugin)

    # The main route must be imported before the application-level plug-in route injection after the extension-level plug-in route injection.
    from backend.app.router import router as main_router

    for plugin in app_plugins:
        inject_app_router(plugin, main_router)

    return main_router


def _ensure_pip_available() -> bool:
    """Make sure pip is available in the virtual environment"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try using ensurepip
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'ensurepip', '--default-pip'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try downloading and installing
    try:
        import os
        import tempfile

        import httpx

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                with httpx.Client(timeout=3) as client:
                    get_pip_url = 'https://bootstrap.pypa.io/get-pip.py'
                    response = client.get(get_pip_url)
                    response.raise_for_status()
                    f.write(response.text)
                    temp_file = f.name
        except Exception:  # noqa: ignore
            return False

        try:
            subprocess.check_call([sys.executable, temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
    except Exception:  # noqa: ignore
        pass

    return False


def install_requirements(plugin: str | None) -> None:  # noqa: C901
    """
    Install plugin dependencies

    :param plugin: Specify the plugin name, otherwise check all plugins
    :return:
    """
    plugins = [plugin] if plugin else get_plugins()

    for plugin in plugins:
        requirements_file = PLUGIN_DIR / plugin / 'requirements.txt'
        missing_dependencies = False
        if os.path.exists(requirements_file):
            with open(requirements_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        req = Requirement(line)
                        dependency = req.name.lower()
                    except Exception as e:
                        raise PluginInstallError(f'Plugin {plugin} Dependency {line} Format error: {e!s}') from e
                    try:
                        distribution(dependency)
                    except PackageNotFoundError:
                        missing_dependencies = True

        if missing_dependencies:
            try:
                if not _ensure_pip_available():
                    raise PluginInstallError(f'pip The installation failed and cannot continue to install the plugin {plugin} dependencies')

                pip_install = [sys.executable, '-m', 'pip', 'install', '-r', requirements_file]
                if settings.PLUGIN_PIP_CHINA:
                    pip_install.extend(['-i', settings.PLUGIN_PIP_INDEX_URL])

                max_retries = settings.PLUGIN_PIP_MAX_RETRY
                for attempt in range(max_retries):
                    try:
                        subprocess.check_call(
                            pip_install,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        break
                    except subprocess.TimeoutExpired:
                        if attempt == max_retries - 1:
                            raise PluginInstallError(f'Plug-in {plugin} depends on installation timeout')
                        continue
                    except subprocess.CalledProcessError as e:
                        if attempt == max_retries - 1:
                            raise PluginInstallError(f'Plug-in {plugin} dependency installation failed: {e}') from e
                        continue
            except subprocess.CalledProcessError as e:
                raise PluginInstallError(f'Plugin {plugin} Dependency installation failed: {e}') from e


def uninstall_requirements(plugin: str) -> None:
    """
    Uninstall plugin dependencies

    :param plugin: plugin name
    :return:
    """
    requirements_file = PLUGIN_DIR / plugin / 'requirements.txt'
    if os.path.exists(requirements_file):
        try:
            pip_uninstall = [sys.executable, '-m', 'pip', 'uninstall', '-r', requirements_file, '-y']
            subprocess.check_call(pip_uninstall, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise PluginInstallError(f'Plugin {plugin} Dependency uninstall failed: {e}') from e


async def install_requirements_async(plugin: str | None = None) -> None:
    """
    Asynchronous installation of plug-in dependencies

    Due to Windows platform limitations, a perfect fully asynchronous solution cannot be implemented. Details:
    https://stackoverflow.com/questions/44633458/why-am-i-getting-notimplementederror-with-async-and-await-on-windows
    """
    await run_in_threadpool(install_requirements, plugin)


async def uninstall_requirements_async(plugin: str) -> None:
    """
    Asynchronous uninstall plug-in dependencies

    :param plugin: plugin name
    :return:
    """
    await run_in_threadpool(uninstall_requirements, plugin)


class PluginStatusChecker:
    """Plugin Status Checker"""

    def __init__(self, plugin: str) -> None:
        """
        Initialize the plug-in status checker

        :param plugin: plugin name
        :return:
        """
        self.plugin = plugin

    async def __call__(self, request: Request) -> None:
        """
        Verify plugin status

        :param request: FastAPI request object
        :return:
        """
        plugin_info = await redis_client.get(f'{settings.PLUGIN_REDIS_PREFIX}:{self.plugin}')
        if not plugin_info:
            log.error('Plugin status is not initialized or lost, and the service needs to be restarted and repaired automatically')
            raise PluginInjectError('Plugin status is not initialized or lost, please contact the system administrator')

        if not int(json.loads(plugin_info)['plugin']['enable']):
            raise errors.ServerError(msg=f'Plugin {self.plugin} is not enabled, please contact the system administrator')
