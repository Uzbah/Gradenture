from enum import StrEnum


class _StrEnum(StrEnum):
    """Base for the project's string enums.

    Members serialize as their value, so schemas declaring these types produce the
    same JSON the database columns already hold.
    """

    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]


class ContentStatus(_StrEnum):
    """Moderation state of user-submitted questions and reviews."""

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    NEEDS_EDIT = 'needs_edit'


class ModerationDecision(_StrEnum):
    """The statuses an admin may move submitted content to."""

    APPROVED = 'approved'
    REJECTED = 'rejected'
    NEEDS_EDIT = 'needs_edit'


class CompanyStatus(_StrEnum):
    """Registry state of a company."""

    PENDING = 'pending'
    APPROVED = 'approved'


class CompanyDecision(_StrEnum):
    """The statuses an admin may move a company or a company edit request to."""

    APPROVED = 'approved'
    REJECTED = 'rejected'


class ContentType(_StrEnum):
    """What a content flag points at."""

    QUESTION = 'question'
    REVIEW = 'review'


class FlagDecision(_StrEnum):
    """How an admin closed a flag."""

    RESOLVED = 'resolved'
    DISMISSED = 'dismissed'


class UserRole(_StrEnum):
    """Platform-wide role, authoritative in public.users.role."""

    USER = 'user'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

    @classmethod
    def admin_roles(cls) -> tuple['UserRole', ...]:
        return cls.ADMIN, cls.SUPER_ADMIN


class ApplicationStatus(_StrEnum):
    """Column of the application tracker kanban."""

    APPLIED = 'applied'
    INTERVIEW = 'interview'
    OFFER = 'offer'
    REJECTED = 'rejected'
    CLOSED = 'closed'


class QuestionType(_StrEnum):
    TECHNICAL = 'technical'
    BEHAVIOURAL = 'behavioural'
    HR = 'hr'
    CASE_STUDY = 'case_study'


class Difficulty(_StrEnum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


class InterviewOutcome(_StrEnum):
    OFFER = 'offer'
    REJECTED = 'rejected'
    GHOSTED = 'ghosted'
    WITHDREW = 'withdrew'
    PENDING = 'pending'


class SkillLevel(_StrEnum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'


class UserGoal(_StrEnum):
    FIRST_JOB = 'first_job'
    SWITCH_CAREER = 'switch_career'
    LEVEL_UP = 'level_up'
    INTERNSHIP = 'internship'
