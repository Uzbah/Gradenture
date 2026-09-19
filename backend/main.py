import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.dependencies.exceptions import AppError
from src.dependencies.rate_limit import limiter
from src.routers import api_router

# Explicit path: load_dotenv() alone resolves from the CWD, so starting the
# server from another directory silently loads the wrong .env (or none).
load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CareerBridge API",
    description="CareerBridge REST API",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"] if os.getenv("NODE_ENV") == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/v1")
def api_root() -> dict:
    return {
        "message": "CareerBridge API v1",
        "docs":    "/docs",
        "auth":    "/api/v1/auth/login",
    }


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.body)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = err.get("loc", ())
        field = str(loc[-1]) if loc else "body"
        errors.setdefault(field, []).append(err.get("msg", "invalid"))
    return JSONResponse(status_code=400, content={"errors": errors})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    if exc.status_code == 405:
        return JSONResponse(status_code=405, content={"error": "Method not allowed"})
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(detail)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3001))
    reload = os.getenv("NODE_ENV") == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
