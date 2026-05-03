import re
from typing import Literal, Optional
from pydantic import BaseModel, field_validator


class ReviewSchema(BaseModel):
    company_id:     str
    domain_id:      Optional[str] = None
    role_title:     str
    review_text:    str
    interview_date: str
    difficulty:     Optional[Literal["easy", "medium", "hard"]] = None
    outcome:        Optional[Literal["offer", "rejected", "ghosted", "withdrew", "pending"]] = None
    is_anonymous:   bool = False

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("must be at least 50 characters")
        return v

    @field_validator("interview_date")
    @classmethod
    def validate_interview_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-01$", v):
            raise ValueError("must be YYYY-MM-01")
        return v

    @field_validator("role_title")
    @classmethod
    def validate_role_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        if len(v) > 100:
            raise ValueError("must be at most 100 characters")
        return v
