import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.common.log import log


class AccessMiddleware(BaseHTTPMiddleware):
    """Log one line per request: method, path, status and elapsed time."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        log.info(
            '{} | {} {} | {} | {:.2f}ms',
            getattr(request.state, 'ip', 'unknown'),
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
