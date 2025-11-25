import importlib
import inspect

from functools import lru_cache
from typing import Any, TypeVar

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


def get_model_objects(module_path: str) -> list[type] | None:
    """
    Get the model object

    :param module_path: Module path
    :return:
    """
    try:
        module = import_module_cached(module_path)
    except ModuleNotFoundError:
        log.warning(f'The module {module_path} does not contain model objects')
        return None
    except Exception:
        raise

    classes = []

    for _name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and module_path in obj.__module__:
            classes.append(obj)

    return classes
