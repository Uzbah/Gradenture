from typing import Literal, Optional
from pydantic import BaseModel, field_validator


class ApplicationSchema(BaseModel):
    company_name: str
    role_title:   str
    status:       Literal["applied", "interview", "offer", "rejected", "closed"] = "applied"
    applied_date: Optional[str] = None
    deadline:     Optional[str] = None
    job_url:      Optional[str] = None
    notes:        Optional[str] = None

    @field_validator("company_name", "role_title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class ApplicationUpdateSchema(BaseModel):
    company_name: Optional[str] = None
    role_title:   Optional[str] = None
    status:       Optional[Literal["applied", "interview", "offer", "rejected", "closed"]] = None
    applied_date: Optional[str] = None
    deadline:     Optional[str] = None
    job_url:      Optional[str] = None
    notes:        Optional[str] = None
