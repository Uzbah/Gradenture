from pydantic import Field, field_validator

from backend.common.schema import SchemaBase


class CreateFlagParam(SchemaBase):
    """Report a question or review to the moderators."""

    reason: str = Field(description='Why the content should be reviewed')

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError('must be at least 5 characters')
        return v.strip()
