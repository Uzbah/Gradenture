from backend.app.admin.crud.crud_flag import flag_dao
from backend.app.career.crud.crud_review import review_dao
from backend.app.career.schema.flag import CreateFlagParam
from backend.app.career.schema.review import CreateReviewParam
from backend.app.career.service.question_service import hide_anonymous
from backend.common.dataclasses import CurrentUser
from backend.common.enums import ContentStatus, ContentType
from backend.common.exception import errors
from backend.common.pagination import PageData, PageParams, paginate
from backend.utils.sanitize import clean_text


class ReviewService:
    """Interview experience write-ups: browsing, submission and flags."""

    @staticmethod
    def get(*, pk: str) -> dict:
        """One approved review.

        :param pk: review ID
        """
        review = review_dao.get_approved(pk)
        if not review:
            raise errors.NotFoundError(msg='Review not found')
        return hide_anonymous(review)

    @staticmethod
    def get_list(
        *,
        params: PageParams,
        company_id: str | None = None,
        domain_id: str | None = None,
    ) -> PageData:
        """One page of approved reviews.

        :param params: page and size
        :param company_id: restrict to one company
        :param domain_id: restrict to one domain
        """
        query = review_dao.select_approved(company_id, domain_id)
        page = paginate(query, params)
        page.items = [hide_anonymous(row) for row in page.items]
        return page

    @staticmethod
    def create(*, user: CurrentUser, obj: CreateReviewParam) -> dict:
        """Submit a review for moderation.

        :param user: the submitter
        :param obj: the review
        """
        payload = obj.model_dump()
        review = review_dao.create(
            {
                **payload,
                'review_text': clean_text(payload['review_text']),
                'submitted_by': user.sub,
                'status': ContentStatus.PENDING,
            }
        )
        return {
            'id': review['id'],
            'status': ContentStatus.PENDING,
            'message': 'Review submitted for moderation',
        }

    @staticmethod
    def flag(*, user: CurrentUser, pk: str, obj: CreateFlagParam) -> None:
        """Report a review to the moderators.

        :param user: the reporter
        :param pk: review ID
        :param obj: the reason
        """
        flag_dao.create(user.sub, ContentType.REVIEW, pk, obj.reason)


review_service: ReviewService = ReviewService()
