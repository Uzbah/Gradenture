from pydantic import Field

from backend.common.enums import ContentType, FlagDecision, ModerationDecision
from backend.common.schema import SchemaBase


class ModerateParam(SchemaBase):
    """An admin's decision on a submitted question or review."""

    status: ModerationDecision = Field(description='Decision')
    admin_note: str | None = Field(None, description='Explanation shown to the submitter')


class FlagDecisionParam(SchemaBase):
    """An admin's decision on a reported piece of content."""

    status: FlagDecision = Field(description='How the flag was closed')


class GetQueueDetail(SchemaBase):
    """Everything waiting for a moderator."""

    questions: list[dict] = Field([], description='Questions awaiting review')
    reviews: list[dict] = Field([], description='Reviews awaiting review')
    companies: list[dict] = Field([], description='Companies awaiting approval')


class GetFlagDetail(SchemaBase):
    """An open flag, with the content it points at."""

    id: str = Field(description='Flag ID')
    reported_by: str = Field(description='Who reported it')
    content_type: ContentType = Field(description='What kind of content')
    content_id: str = Field(description='ID of the reported content')
    reason: str = Field(description='Why it was reported')
    status: str = Field(description='Flag status')
    created_at: str = Field(description='When it was reported')
    content: dict | None = Field(None, description='The reported content, or null if it is gone')
