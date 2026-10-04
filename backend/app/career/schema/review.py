import re

from pydantic import Field, field_validator

from backend.common.enums import ContentStatus, Difficulty, InterviewOutcome
from backend.common.schema import SchemaBase

MONTH_DATE_RE = re.compile(r'^\d{4}-\d{2}-01$')


class ReviewSchemaBase(SchemaBase):
    """Fields a submitter provides."""

    company_id: str = Field(description='Company the interview was with')
    domain_id: str | None = Field(None, description='Domain the role belongs to')
    role_title: str = Field(description='Role interviewed for')
    review_text: str = Field(description='The write-up of the interview')
    interview_date: str = Field(description='Month of the interview, as YYYY-MM-01')
    difficulty: Difficulty | None = Field(None, description='How hard the process was')
    outcome: InterviewOutcome | None = Field(None, description='How the process ended')
    is_anonymous: bool = Field(False, description='Hide the submitter from other users')

    @field_validator('review_text')
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError('must be at least 50 characters')
        return v

    @field_validator('interview_date')
    @classmethod
    def validate_interview_date(cls, v: str) -> str:
        if not MONTH_DATE_RE.match(v):
            raise ValueError('must be YYYY-MM-01')
        return v

    @field_validator('role_title')
    @classmethod
    def validate_role_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('must not be empty')
        if len(v) > 100:
            raise ValueError('must be at most 100 characters')
        return v


class CreateReviewParam(ReviewSchemaBase):
    """Submit a review for moderation."""


class GetReviewDetail(SchemaBase):
    """A review as returned to a reader."""

    id: str = Field(description='Review ID')
    company_id: str = Field(description='Company ID')
    domain_id: str | None = Field(None, description='Domain ID')
    role_title: str = Field(description='Role interviewed for')
    review_text: str = Field(description='The write-up')
    interview_date: str = Field(description='Month of the interview')
    difficulty: Difficulty | None = Field(None, description='How hard the process was')
    outcome: InterviewOutcome | None = Field(None, description='How the process ended')
    is_anonymous: bool = Field(False, description='Whether the submitter is hidden')
    status: ContentStatus = Field(description='Moderation status')
    admin_note: str | None = Field(None, description='Moderator note, when one was left')
    submitted_by: str | None = Field(None, description='Submitter ID, omitted for anonymous submissions')
    created_at: str = Field(description='When it was submitted')


class CreateReviewDetail(SchemaBase):
    """What the submitter gets back."""

    id: str = Field(description='Review ID')
    status: ContentStatus = Field(description='Moderation status, always pending on submission')
    message: str = Field(description='What happens next')
