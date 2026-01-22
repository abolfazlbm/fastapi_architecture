import importlib
import inspect
import os.path

from functools import lru_cache
from typing import Any, TypeVar

import sqlalchemy as sa

from backend.common.exception import errors
from backend.common.log import log

T = TypeVar('T')


@lru_cache(maxsize=512)
def import_module_cached(module_path: str) -> Any:
    """
    Cache import module

    :param module_path: module path
    :return:
    """
    return importlib.import_module(module_path)


def dynamic_import_data_model(module_path: str) -> type[T]:
    """
    Dynamic import of data models

    :param module_path: module path, format 'module_path.class_name'
    :return:
    """
    try:
        module_path, class_name = module_path.rsplit('.', 1)
        module = import_module_cached(module_path)
        return getattr(module, class_name)
    except Exception as e:
        log.error(f'Dynamic import of data model failed：{e}')
        raise errors.ServerError(msg='Dynamic analysis of data model column failed, please contact the system super administrator')


def get_model_objects(module_path: str) -> list[object] | None:
    """
    Get the model object

    :param module_path: Module path
    :return:
    """
    try:
        module = import_module_cached(module_path)
    except ModuleNotFoundError:
        return None
    except Exception as e:
        raise e from None

    classes = []

    for _name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) and module_path in obj.__module__) or (
            isinstance(obj, sa.Table) and obj.metadata is not None
        ):
            classes.append(obj)

    return classes


def get_app_models() -> list[object]:
    """Get all model classes of app"""
    from backend.core.path_conf import BASE_PATH

    app_path = BASE_PATH / 'app'
    list_dirs = os.listdir(app_path)

    apps = [d for d in list_dirs if os.path.isdir(os.path.join(app_path, d)) and d != '__pycache__']

    objs = []
    for app in apps:
        module_path = f'backend.app.{app}.model'
        model_objs = get_model_objects(module_path)
        if model_objs:
            objs.extend(model_objs)

    return objs


@lru_cache
def get_all_models() -> list[object]:
    """Get all model classes"""
    from backend.plugin.core import get_plugin_models

    return get_app_models() + get_plugin_models()
