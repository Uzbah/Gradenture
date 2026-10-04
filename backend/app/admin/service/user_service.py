import bleach

from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.schema.user import OnboardingParam
from backend.common.dataclasses import CurrentUser
from backend.common.exception import errors


class UserService:
    """The caller's own profile, and the domain list onboarding picks from."""

    @staticmethod
    def get_me(*, user: CurrentUser) -> dict:
        """The caller's profile row.

        :param user: the caller
        """
        profile = user_dao.get_by_id(user.sub)
        if not profile:
            raise errors.NotFoundError(msg='User not found')
        return profile

    @staticmethod
    def get_domains() -> list[dict]:
        """Every career domain, by name."""
        return user_dao.get_domains()

    @staticmethod
    def complete_onboarding(*, user: CurrentUser, obj: OnboardingParam) -> dict:
        """Store the onboarding answers.

        University is free text shown back to other users, so it is stripped of
        markup rather than merely tag-stripped.

        :param user: the caller
        :param obj: the answers
        """
        user_dao.upsert_profile(
            {
                'id': user.sub,
                'email': user.email,
                'domain_id': str(obj.domain_id),
                'skill_level': obj.skill_level,
                'goal': obj.goal,
                'university': bleach.clean(obj.university, tags=[], strip=True),
                'onboarding_complete': True,
            }
        )
        return {'message': 'Onboarding complete', 'onboarding_complete': True}


user_service: UserService = UserService()
