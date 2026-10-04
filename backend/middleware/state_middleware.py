from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.utils.trace_id import TRACE_ID_HEADER, set_trace_id, trace_id_from_request


class StateMiddleware(BaseHTTPMiddleware):
    """Attach a trace id and the caller's IP to the request.

    Runs before everything else that logs, so every line of a request — including
    the access log and any exception — carries the same id. The id is echoed back
    in the response headers so a user can quote it in a bug report.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = trace_id_from_request(request)
        set_trace_id(trace_id)

        request.state.trace_id = trace_id
        request.state.ip = self._client_ip(request)

        response = await call_next(request)
        response.headers[TRACE_ID_HEADER] = trace_id
        return response

    @staticmethod
    def _client_ip(request: Request) -> str:
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'
