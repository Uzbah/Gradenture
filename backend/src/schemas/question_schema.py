import re
from typing import Literal, Optional
from pydantic import BaseModel, field_validator


class QuestionSchema(BaseModel):
    domain_id:     str
    company_id:    str
    role_title:    str
    question_text: str
    question_type: Literal["technical", "behavioural", "hr", "case_study"]
    difficulty:    Literal["easy", "medium", "hard"]
    asked_date:    str
    notes:         Optional[str] = None
    is_anonymous:  bool = False

    @field_validator("question_text")
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        if len(v) < 20:
            raise ValueError("must be at least 20 characters")
        return v

    @field_validator("asked_date")
    @classmethod
    def validate_asked_date(cls, v: str) -> str:
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


class QuestionEditSchema(BaseModel):
    question_text: Optional[str] = None
    notes:         Optional[str] = None

    @field_validator("question_text")
    @classmethod
    def validate_question_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 20:
            raise ValueError("must be at least 20 characters")
        return v


class FlagSchema(BaseModel):
    reason: str

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError("must be at least 5 characters")
        return v.strip()
