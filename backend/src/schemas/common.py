from datetime import date
from typing import Annotated
from urllib.parse import urlparse

from pydantic import AfterValidator, StringConstraints

# Plain str (not uuid.UUID) on purpose: services compare ids with == and send
# them to supabase-py as JSON, both of which need strings. Malformed ids are
# rejected as 400 here instead of reaching Postgres as a 500.
UUIDStr = Annotated[
    str,
    StringConstraints(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    ),
]


def _http_url(v: str) -> str:
    v = v.strip()
    parsed = urlparse(v)
    # Rendered as <a href>: anything but http(s) (javascript:, data:) is XSS.
    if parsed.scheme not in ("http", "https") or not parsed.netloc or len(v) > 500:
        raise ValueError("must be an http(s) URL")
    return v


HttpUrlStr = Annotated[str, AfterValidator(_http_url)]


def _iso_date(v: str) -> str:
    try:
        date.fromisoformat(v)
    except ValueError:
        raise ValueError("must be a valid YYYY-MM-DD date") from None
    return v


def _first_of_month(v: str) -> str:
    if not v.endswith("-01") or len(v) != 10:
        raise ValueError("must be YYYY-MM-01")
    return _iso_date(v)


DateStr = Annotated[str, AfterValidator(_iso_date)]
MonthStr = Annotated[str, AfterValidator(_first_of_month)]
