import inspect

from typing import Any

from fastapi import FastAPI

from backend.common.enums import LifespanStage
from backend.common.lifespan import lifespan_manager
from backend.common.log import log
from backend.plugin.core import get_ordered_enabled_plugins
from backend.plugin.errors import PluginInjectError
from backend.utils.async_helper import run_await
from backend.utils.dynamic_import import import_module_cached


def register_plugin_lifespan_hook(plugin: str, module: Any) -> None:
    """
    Register a plugin lifespan hook

    :param plugin: Plugin Name
    :param module: Plugin hooks module
    :return:
    """
    lifespan_hook = getattr(module, 'lifespan', None)
    if lifespan_hook is None:
        return

    if not callable(lifespan_hook):
        log.warning(f'Plugin {plugin}  lifespan is not callable and was skipped')
        return

    lifespan_manager.register(lifespan_hook, stage=LifespanStage.plugin)  # type: ignore[call-overload]
    log.info(f'Plugin {plugin} lifespan hook registered successfully')


def run_plugin_setup_hook(plugin: str, module: Any, app: FastAPI) -> None:
    """
    Execute a plugin setup hook

    :param plugin: Plugin Name
    :param module: Plugin hooks module
    :param app: FastAPI application instance
    :return:
    """
    setup_hook = getattr(module, 'setup', None)
    if setup_hook is None:
        return

    if not callable(setup_hook):
        log.warning(f'Plugin {plugin}  setup is not callable and was skipped')
        return

    setup_result = setup_hook(app)
    if inspect.isawaitable(setup_result):
        run_await(lambda: setup_result)()  # type: ignore
    log.info(f'Plugin {plugin} setup hook executed successfully')


def run_plugin_otel_hook(plugin: str, module: Any, app: FastAPI) -> None:
    """
    Execute a plugin OpenTelemetry hook

    :param plugin: Plugin Name
    :param module: Plugin hooks module
    :param app: FastAPI application instance
    :return:
    """
    otel_hook = getattr(module, 'otel', None)
    if otel_hook is None:
        return

    if not callable(otel_hook):
        log.warning(f'Plugin {plugin}  otel hook is not callable and was skipped')
        return

    otel_result = otel_hook(app)
    if inspect.isawaitable(otel_result):
        run_await(lambda: otel_result)()  # type: ignore
    log.info(f'Plugin {plugin} otel hook executed successfully')


def _get_plugin_hook_modules() -> list[tuple[str, Any]]:
    """
    Get the plugin hooks module

    :return:
    """
    plugin_hook_modules: list[tuple[str, Any]] = []

    for plugin in get_ordered_enabled_plugins():
        module_path = f'backend.plugin.{plugin.name}.hooks'
        try:
            module = import_module_cached(module_path)
        except ModuleNotFoundError as e:
            if e.name == module_path:
                continue
            log.warning(f'Plugin {plugin.name} hooks failed to load: {e}')
            continue
        except Exception as e:
            log.warning(f'Plugin {plugin.name} hooks failed to load: {e}')
            continue

        plugin_hook_modules.append((plugin.name, module))

    return plugin_hook_modules


def register_plugin_hooks(app: FastAPI) -> None:
    """
    Register and execute plugin hooks

    :param app: FastAPI application instance
    :return:
    """

    def run_setup_hook(plugin: str, module: Any) -> None:
        try:
            register_plugin_lifespan_hook(plugin, module)
        except Exception as e:
            log.exception(f'Plugin {plugin} lifespan hooks failed: {e}')
            raise PluginInjectError(f'Plugin {plugin} lifespan hooks failed:{e!s}') from e
        try:
            run_plugin_setup_hook(plugin, module, app)
        except Exception as e:
            log.exception(f'Plugin {plugin} setup hooks failed: {e}')
            raise PluginInjectError(f'Plugin {plugin} setup hooks failed:{e!s}') from e

    for plugin, module in _get_plugin_hook_modules():
        run_setup_hook(plugin, module)


def init_plugin_otel_hooks(app: FastAPI) -> None:
    """
    Initialize plugin OpenTelemetry hooks

    :param app: FastAPI application instance
    :return:
    """

    def run_otel_hook(plugin: str, module: Any) -> None:
        try:
            run_plugin_otel_hook(plugin, module, app)
        except Exception as e:
            log.exception(f'Plugin {plugin} otel hook failed: {e}')
            raise PluginInjectError(f'Plugin {plugin} otel hook failed:{e!s}') from e

    for plugin, module in _get_plugin_hook_modules():
        run_otel_hook(plugin, module)
