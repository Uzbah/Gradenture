from typing import Literal, Optional
from pydantic import BaseModel, field_validator

from src.schemas.common import MonthStr, UUIDStr


class ReviewSchema(BaseModel):
    company_id:     UUIDStr
    domain_id:      Optional[UUIDStr] = None
    role_title:     str
    review_text:    str
    interview_date: MonthStr
    difficulty:     Optional[Literal["easy", "medium", "hard"]] = None
    outcome:        Optional[Literal["offer", "rejected", "ghosted", "withdrew", "pending"]] = None
    is_anonymous:   bool = False

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("must be at least 50 characters")
        return v

    @field_validator("role_title")
    @classmethod
    def validate_role_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        if len(v) > 100:
            raise ValueError("must be at most 100 characters")
        return v


class ReviewEditSchema(BaseModel):
    review_text: str

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("must be at least 50 characters")
        return v
