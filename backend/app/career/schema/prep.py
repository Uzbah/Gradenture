from pydantic import Field

from backend.common.schema import SchemaBase


class ToggleTopicParam(SchemaBase):
    """Mark a roadmap topic done or not done."""

    topic: str = Field(description='Topic name, which must be on the caller\'s roadmap')
    completed: bool = Field(description='New state')


class PrepTopicDetail(SchemaBase):
    """One topic on the roadmap."""

    topic: str = Field(description='Topic name')
    completed: bool = Field(description='Whether the caller has marked it done')


class GetPrepDetail(SchemaBase):
    """The caller's roadmap and preparedness score."""

    domain_id: str = Field(description='Domain the roadmap belongs to')
    topics: list[PrepTopicDetail] = Field([], description='Topics, in roadmap order')
    score: int = Field(0, description='Percentage of topics completed')
