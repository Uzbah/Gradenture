from fastapi import FastAPI
from fastapi.routing import APIRoute


def ensure_unique_route_names(app: FastAPI) -> None:
    """Fail loudly at startup if two routes share a function name.

    Duplicate names silently collide in the generated OpenAPI schema and in any
    client generated from it.
    """
    seen: set[str] = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in seen:
                raise ValueError(f'Duplicate route function name: {route.name}')
            seen.add(route.name)


def simplify_operation_ids(app: FastAPI) -> None:
    """Use the route's function name as its operation id.

    FastAPI's default is the function name plus the path and method, which makes
    generated clients unreadable.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name
