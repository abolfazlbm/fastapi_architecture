from fastapi import FastAPI
from fastapi.routing import APIRoute


def simplify_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation ID so that the generated client has a simpler API function name

    :param app: FastAPI application example
    :return:
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    Check if route name is unique

    :param app: FastAPI application example
    :return:
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'Non-unique route name: {route.name}')
            temp_routes.add(route.name)
