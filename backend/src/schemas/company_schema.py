from pydantic import BaseModel
from typing import Literal, Optional

from src.schemas.common import HttpUrlStr, UUIDStr


class CompanySchema(BaseModel):
    name:     str
    website:  Optional[HttpUrlStr] = None
    industry: Optional[str] = None


class CompanyAdminCreateSchema(BaseModel):
    name:     str
    website:  Optional[HttpUrlStr] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrlStr] = None


class CompanyUpdateSchema(BaseModel):
    """All optional: an empty body still approves, keeping the old behaviour."""
    name:     Optional[str] = None
    website:  Optional[HttpUrlStr] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrlStr] = None
    status:   Optional[Literal["pending", "approved"]] = None


class CompanyMergeSchema(BaseModel):
    into_id: UUIDStr


class CompanyManagerGrantSchema(BaseModel):
    email: str


class CompanyEditRequestSchema(BaseModel):
    """What a company manager may propose. Deliberately excludes `status` —
    managers can never approve their own company or touch its content."""
    name:     Optional[str] = None
    website:  Optional[HttpUrlStr] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrlStr] = None


class CompanyEditDecisionSchema(BaseModel):
    status:     Literal["approved", "rejected"]
    admin_note: Optional[str] = None
