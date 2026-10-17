from typing import Literal, Optional
from pydantic import BaseModel, field_validator

from src.schemas.common import DateStr, HttpUrlStr

Status = Literal["applied", "interview", "offer", "rejected", "closed"]


class ApplicationSchema(BaseModel):
    company_name: str
    role_title:   str
    status:       Status = "applied"
    applied_date: Optional[DateStr] = None
    deadline:     Optional[DateStr] = None
    job_url:      Optional[HttpUrlStr] = None
    notes:        Optional[str] = None

    @field_validator("company_name", "role_title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class ApplicationUpdateSchema(BaseModel):
    """Partial update: omitted fields are untouched, an explicit null clears
    the optional ones (dates, link, notes)."""
    company_name: Optional[str] = None
    role_title:   Optional[str] = None
    status:       Optional[Status] = None
    applied_date: Optional[DateStr] = None
    deadline:     Optional[DateStr] = None
    job_url:      Optional[HttpUrlStr] = None
    notes:        Optional[str] = None

    @field_validator("company_name", "role_title", "status")
    @classmethod
    def required_if_sent(cls, v: Optional[str]) -> Optional[str]:
        # Runs only for values actually sent; these columns are NOT NULL.
        if v is None or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()
