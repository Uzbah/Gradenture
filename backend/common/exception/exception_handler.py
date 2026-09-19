from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.common.exception.errors import BaseExceptionError, CustomError
from backend.common.log import log
from backend.common.response.response_code import CustomResponseCode, StandardResponseCode


def _envelope(*, http_code: int, code: int, msg: str, data: object = None) -> JSONResponse:
    """Every error leaves the app in the same shape a success does."""
    return JSONResponse(status_code=http_code, content={'code': code, 'msg': msg, 'data': data})


def _validation_fields(exc: RequestValidationError | ValidationError) -> dict[str, list[str]]:
    """Flatten pydantic errors to ``{field: [message, ...]}``.

    The frontend renders this map directly, so the shape is part of the API contract.
    """
    fields: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = err.get('loc', ())
        # Drop the 'body'/'query' prefix pydantic puts first; keep the field name.
        field = str(loc[-1]) if loc else 'body'
        fields.setdefault(field, []).append(err.get('msg', 'invalid'))
    return fields


def register_exception(app: FastAPI) -> None:
    """Register every exception handler on the app."""

    @app.exception_handler(CustomError)
    async def custom_error_handler(_request: Request, exc: CustomError) -> JSONResponse:
        return _envelope(http_code=exc.http_code, code=exc.code, msg=exc.msg or '', data=exc.data)

    @app.exception_handler(BaseExceptionError)
    async def base_error_handler(_request: Request, exc: BaseExceptionError) -> JSONResponse:
        return _envelope(http_code=exc.code, code=exc.code, msg=exc.msg or '', data=exc.data)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = _validation_fields(exc)
        return _envelope(
            http_code=StandardResponseCode.HTTP_400,
            code=CustomResponseCode.HTTP_422.code,
            msg=CustomResponseCode.HTTP_422.msg,
            data=fields,
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        # A response model failing validation is a bug on our side, not the caller's.
        log.error('Response validation failed: {}', exc)
        return _envelope(
            http_code=StandardResponseCode.HTTP_500,
            code=CustomResponseCode.HTTP_500.code,
            msg=CustomResponseCode.HTTP_500.msg,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail
        msg = detail if isinstance(detail, str) else str(detail)
        return _envelope(http_code=exc.status_code, code=exc.status_code, msg=msg)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(_request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return _envelope(
            http_code=StandardResponseCode.HTTP_429,
            code=CustomResponseCode.HTTP_429.code,
            msg=f'{CustomResponseCode.HTTP_429.msg}: {exc.detail}',
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        log.exception('Unhandled exception: {}', exc)
        return _envelope(
            http_code=StandardResponseCode.HTTP_500,
            code=CustomResponseCode.HTTP_500.code,
            msg=CustomResponseCode.HTTP_500.msg,
        )
