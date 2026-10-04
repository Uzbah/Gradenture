from typing import Any

from fastapi import HTTPException

from backend.common.response.response_code import CustomErrorCode, StandardResponseCode


class BaseExceptionError(Exception):
    """Base for the project's service-layer exceptions.

    Services raise these; the handlers in ``exception_handler.py`` turn them into the
    unified ``{code, msg, data}`` envelope with the matching HTTP status. Nothing in
    the service layer imports FastAPI.
    """

    code: int

    def __init__(self, *, msg: str | None = None, data: Any = None) -> None:
        self.msg = msg
        self.data = data
        super().__init__(msg)


class HTTPError(HTTPException):
    """Raised where FastAPI's own machinery must see an HTTPException."""

    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionError):
    """Error carrying one of the application-specific codes in ``CustomErrorCode``.

    The body's ``code`` is the fine-grained code; ``http_code`` is the status sent.
    """

    def __init__(
        self, *, error: CustomErrorCode, http_code: int = StandardResponseCode.HTTP_400, data: Any = None
    ) -> None:
        self.code = error.code
        self.http_code = http_code
        super().__init__(msg=error.msg, data=data)


class RequestError(BaseExceptionError):
    """The request was malformed or failed a business rule (400)."""

    code = StandardResponseCode.HTTP_400

    def __init__(self, *, msg: str = 'Bad request', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class ForbiddenError(BaseExceptionError):
    """The caller is authenticated but not allowed to do this (403)."""

    code = StandardResponseCode.HTTP_403

    def __init__(self, *, msg: str = 'Forbidden', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class NotFoundError(BaseExceptionError):
    """The addressed resource does not exist, or is not visible to the caller (404)."""

    code = StandardResponseCode.HTTP_404

    def __init__(self, *, msg: str = 'Not found', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class PayloadTooLargeError(BaseExceptionError):
    """The uploaded body is larger than the endpoint accepts (413)."""

    code = StandardResponseCode.HTTP_413

    def __init__(self, *, msg: str = 'Payload too large', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class UnprocessableError(BaseExceptionError):
    """The request was well-formed but its content could not be used (422)."""

    code = StandardResponseCode.HTTP_422

    def __init__(self, *, msg: str = 'Unprocessable content', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class ConflictError(BaseExceptionError):
    """The write conflicts with existing state (409)."""

    code = StandardResponseCode.HTTP_409

    def __init__(self, *, msg: str = 'Conflict', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class ServerError(BaseExceptionError):
    """Something the caller cannot fix went wrong (500)."""

    code = StandardResponseCode.HTTP_500

    def __init__(self, *, msg: str = 'Internal server error', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class GatewayError(BaseExceptionError):
    """An upstream service (Supabase, Gemini, SMTP) failed (502)."""

    code = StandardResponseCode.HTTP_502

    def __init__(self, *, msg: str = 'Bad gateway', data: Any = None) -> None:
        super().__init__(msg=msg, data=data)


class TokenError(HTTPError):
    """The access token is missing, expired or unverifiable (401)."""

    code = StandardResponseCode.HTTP_401

    def __init__(self, *, msg: str = 'Not authenticated', headers: dict[str, Any] | None = None) -> None:
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})
