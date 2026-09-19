import uuid
from contextvars import ContextVar

from starlette.requests import Request

# Set by StateMiddleware at the start of every request, read by the logger.
_trace_id: ContextVar[str] = ContextVar('trace_id', default='-')

TRACE_ID_HEADER = 'X-Request-ID'


def new_trace_id() -> str:
    return uuid.uuid4().hex[:16]


def get_trace_id() -> str:
    return _trace_id.get()


def set_trace_id(value: str) -> None:
    _trace_id.set(value)


def trace_id_from_request(request: Request) -> str:
    """Reuse an inbound request id when a proxy supplied one, else mint a new one."""
    return request.headers.get(TRACE_ID_HEADER) or new_trace_id()
