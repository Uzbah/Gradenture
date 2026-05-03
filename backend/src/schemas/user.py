from typing import Literal
from uuid import UUID
from pydantic import BaseModel, field_validator


class OnboardingSchema(BaseModel):
    domain_id:   UUID
    skill_level: Literal["beginner", "intermediate", "advanced"]
    goal:        Literal["first_job", "switch_career", "level_up", "internship"]
    university:  str

    @field_validator("university")
    @classmethod
    def validate_university(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("must be at most 100 characters")
        return v
