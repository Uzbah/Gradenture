import re

from pydantic import Field, field_validator

from backend.common.enums import ContentStatus, Difficulty, QuestionType
from backend.common.schema import SchemaBase

# Questions are filed by the month they were asked, not the exact day: the form
# sends an <input type="month"> value normalised to the first of the month.
MONTH_DATE_RE = re.compile(r'^\d{4}-\d{2}-01$')


class QuestionSchemaBase(SchemaBase):
    """Fields a submitter provides."""

    domain_id: str = Field(description='Domain the role belongs to')
    company_id: str = Field(description='Company the question was asked at')
    role_title: str = Field(description='Role interviewed for')
    question_text: str = Field(description='The question as it was asked')
    question_type: QuestionType = Field(description='Kind of question')
    difficulty: Difficulty = Field(description='How hard the question was')
    asked_date: str = Field(description='Month the question was asked, as YYYY-MM-01')
    notes: str | None = Field(None, description='How the submitter answered, or context')
    is_anonymous: bool = Field(False, description='Hide the submitter from other users')

    @field_validator('question_text')
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        if len(v) < 20:
            raise ValueError('must be at least 20 characters')
        return v

    @field_validator('asked_date')
    @classmethod
    def validate_asked_date(cls, v: str) -> str:
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


class CreateQuestionParam(QuestionSchemaBase):
    """Submit a question for moderation."""


class UpdateQuestionParam(SchemaBase):
    """Edit a question that moderation returned as needs_edit.

    No endpoint uses this yet — resubmission is listed as remaining work in
    backend/CLAUDE.md.
    """

    question_text: str | None = Field(None, description='Revised question text')
    notes: str | None = Field(None, description='Revised notes')

    @field_validator('question_text')
    @classmethod
    def validate_question_text(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 20:
            raise ValueError('must be at least 20 characters')
        return v


class GetQuestionDetail(SchemaBase):
    """A question as returned to a reader.

    Timestamps stay strings: PostgREST already returns them ISO-formatted, and
    re-parsing them here would only risk changing the format the frontend sees.
    """

    id: str = Field(description='Question ID')
    domain_id: str = Field(description='Domain ID')
    company_id: str = Field(description='Company ID')
    role_title: str = Field(description='Role interviewed for')
    question_text: str = Field(description='The question')
    question_type: QuestionType = Field(description='Kind of question')
    difficulty: Difficulty = Field(description='How hard the question was')
    asked_date: str = Field(description='Month the question was asked')
    notes: str | None = Field(None, description='Submitter notes')
    is_anonymous: bool = Field(False, description='Whether the submitter is hidden')
    status: ContentStatus = Field(description='Moderation status')
    admin_note: str | None = Field(None, description='Moderator note, when one was left')
    submitted_by: str | None = Field(None, description='Submitter ID, omitted for anonymous submissions')
    upvotes: int = Field(0, description='Number of upvotes')
    created_at: str = Field(description='When it was submitted')


class CreateQuestionDetail(SchemaBase):
    """What the submitter gets back: the queue position, not the question."""

    id: str = Field(description='Question ID')
    status: ContentStatus = Field(description='Moderation status, always pending on submission')
    message: str = Field(description='What happens next')


class QuestionUpvoteDetail(SchemaBase):
    """Result of toggling an upvote."""

    upvoted: bool = Field(description='Whether the caller now upvotes this question')
    upvotes: int = Field(description='Total upvotes after the toggle')
