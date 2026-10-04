from pydantic import EmailStr, Field

from backend.common.enums import CompanyDecision, CompanyStatus
from backend.common.schema import SchemaBase


class CreateCompanyAdminParam(SchemaBase):
    """Create a company directly, skipping the submission queue."""

    name: str = Field(description='Company name')
    website: str | None = Field(None, description='Company website')
    industry: str | None = Field(None, description='Industry')
    logo_url: str | None = Field(None, description='Logo URL')


class UpdateCompanyParam(SchemaBase):
    """Edit a company, or approve it.

    Every field is optional: an empty body approves a pending company, which is
    what the moderation queue's approve button sends.
    """

    name: str | None = Field(None, description='New name')
    website: str | None = Field(None, description='New website')
    industry: str | None = Field(None, description='New industry')
    logo_url: str | None = Field(None, description='New logo URL')
    status: CompanyStatus | None = Field(None, description='New registry status')


class MergeCompanyParam(SchemaBase):
    """Fold a duplicate company into another."""

    into_id: str = Field(description='ID of the company to keep')


class GrantManagerParam(SchemaBase):
    """Give a user management rights over a company."""

    email: EmailStr = Field(description='Email of the user to grant')


class CompanyEditDecisionParam(SchemaBase):
    """An admin's decision on a proposed profile edit."""

    status: CompanyDecision = Field(description='Decision')
    admin_note: str | None = Field(None, description='Explanation shown to the manager')


class GetManagerDetail(SchemaBase):
    """A user who may edit a company's profile."""

    user_id: str = Field(description='User ID')
    created_at: str = Field(description='When the grant was made')
    users: dict | None = Field(None, description='The granted user, joined for their email')


class GetCompanyEditDetail(SchemaBase):
    """A pending profile edit request."""

    id: str = Field(description='Request ID')
    company_id: str = Field(description='Company the edit is for')
    requested_by: str = Field(description='Manager who proposed it')
    changes: dict = Field(description='Proposed field values')
    status: str = Field(description='Request status')
    created_at: str = Field(description='When it was proposed')
    companies: dict | None = Field(None, description='The company, joined for its name')


class MergeResultDetail(SchemaBase):
    """What a merge moved."""

    merged_from: str = Field(description='ID of the company that was removed')
    merged_name: str = Field(description='Its name')
    into_name: str = Field(description='Name of the company that was kept')
    interview_questions: int = Field(0, description='Questions repointed')
    interview_reviews: int = Field(0, description='Reviews repointed')
