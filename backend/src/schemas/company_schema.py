from pydantic import BaseModel
from typing import Literal, Optional


class CompanySchema(BaseModel):
    name:     str
    website:  Optional[str] = None
    industry: Optional[str] = None


class CompanyAdminCreateSchema(BaseModel):
    name:     str
    website:  Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyUpdateSchema(BaseModel):
    """All optional: an empty body still approves, keeping the old behaviour."""
    name:     Optional[str] = None
    website:  Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    status:   Optional[Literal["pending", "approved"]] = None


class CompanyMergeSchema(BaseModel):
    into_id: str
