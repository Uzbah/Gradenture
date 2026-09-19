from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from backend import __version__
from backend.app.admin.api.router import router as admin_router
from backend.app.career.api.router import router as career_router
from backend.common.exception.exception_handler import register_exception
from backend.common.log import log, setup_logging
from backend.core.conf import settings
from backend.core.path_conf import FRONTEND_DIST_DIR
from backend.database.redis import redis_client
from backend.middleware.access_middleware import AccessMiddleware
from backend.middleware.state_middleware import StateMiddleware
from backend.utils.limiter import limiter
from backend.utils.openapi import ensure_unique_route_names, simplify_operation_ids


@asynccontextmanager
async def register_init(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown."""
    redis_client.open()
    log.info('{} v{} started in {} mode', settings.FASTAPI_TITLE, __version__, settings.ENVIRONMENT)
    try:
        yield
    finally:
        redis_client.close()


def register_app() -> FastAPI:
    """Build the application.

    The single place the app is assembled: middleware, routes, exception handlers
    and static files are each registered by one function below, in this order.
    """
    setup_logging()

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=__version__,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOC_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        lifespan=register_init,
    )

    register_rate_limiter(app)
    register_middleware(app)
    register_router(app)
    register_exception(app)
    register_static_file(app)

    return app


def register_rate_limiter(app: FastAPI) -> None:
    """Expose the limiter to slowapi's decorators, which read it off app state."""
    app.state.limiter = limiter


def register_middleware(app: FastAPI) -> None:
    """Register middleware.

    Starlette runs these in reverse order of registration, so the last one added is
    the outermost: CORS wraps the access log, which wraps the request state.
    """
    app.add_middleware(AccessMiddleware)
    app.add_middleware(StateMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=settings.CORS_EXPOSE_HEADERS,
    )


def register_router(app: FastAPI) -> None:
    """Mount every module's routes under the versioned API prefix."""
    v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)
    v1.include_router(admin_router)
    v1.include_router(career_router)

    @v1.get('', summary='API root', tags=['Meta'])
    def api_root() -> dict:
        return {
            'message': f'{settings.FASTAPI_TITLE} v1',
            'docs': settings.FASTAPI_DOCS_URL,
            'auth': f'{settings.FASTAPI_API_V1_PATH}/auth/login',
        }

    app.include_router(v1)

    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_static_file(app: FastAPI) -> None:
    """Serve the built frontend at / when it is present.

    In production the SPA and the API share an origin, which is why
    CORS_ALLOWED_ORIGINS can be empty there.
    """
    if settings.FASTAPI_SERVE_FRONTEND and FRONTEND_DIST_DIR.exists():
        app.mount('/', StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name='frontend')
