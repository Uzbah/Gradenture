from backend.app.admin.crud.crud_flag import flag_dao
from backend.app.career.crud.crud_question import question_dao
from backend.app.career.schema.flag import CreateFlagParam
from backend.app.career.schema.question import CreateQuestionParam
from backend.common.dataclasses import CurrentUser
from backend.common.enums import ContentStatus, ContentType
from backend.common.exception import errors
from backend.common.pagination import PageData, PageParams, paginate
from backend.utils.sanitize import clean_text


def hide_anonymous(row: dict) -> dict:
    """Null the submitter on a row that was submitted anonymously.

    Applied on the way out rather than at insert time: moderators still need to
    know who wrote a piece of content, readers do not. The field is nulled rather
    than removed because the response schema declares it either way, so removing
    it here would only have it come back as null from the serializer.
    """
    if row.get('is_anonymous'):
        row['submitted_by'] = None
    return row


class QuestionService:
    """Interview questions: browsing, submission, upvotes and flags."""

    @staticmethod
    def get(*, pk: str) -> dict:
        """One approved question.

        :param pk: question ID
        """
        question = question_dao.get_approved(pk)
        if not question:
            raise errors.NotFoundError(msg='Question not found')
        return hide_anonymous(question)

    @staticmethod
    def get_list(
        *,
        params: PageParams,
        domain_id: str | None = None,
        company_id: str | None = None,
        difficulty: str | None = None,
        question_type: str | None = None,
    ) -> PageData:
        """One page of approved questions.

        :param params: page and size
        :param domain_id: restrict to one domain
        :param company_id: restrict to one company
        :param difficulty: restrict to one difficulty
        :param question_type: restrict to one question type
        """
        query = question_dao.select_approved(domain_id, company_id, difficulty, question_type)
        page = paginate(query, params)
        page.items = [hide_anonymous(row) for row in page.items]
        return page

    @staticmethod
    def create(*, user: CurrentUser, obj: CreateQuestionParam) -> dict:
        """Submit a question for moderation.

        :param user: the submitter
        :param obj: the question
        """
        payload = obj.model_dump()
        question = question_dao.create(
            {
                **payload,
                'question_text': clean_text(payload['question_text']),
                'notes': clean_text(payload['notes']) if payload.get('notes') else None,
                'submitted_by': user.sub,
                'status': ContentStatus.PENDING,
            }
        )
        return {
            'id': question['id'],
            'status': ContentStatus.PENDING,
            'message': 'Question submitted for review',
        }

    @staticmethod
    def toggle_upvote(*, user: CurrentUser, pk: str) -> dict:
        """Add or remove the caller's upvote.

        :param user: the voter
        :param pk: question ID
        """
        result = question_dao.toggle_upvote(pk, user.sub)
        if not result:
            raise errors.NotFoundError(msg='Question not found')
        return result

    @staticmethod
    def flag(*, user: CurrentUser, pk: str, obj: CreateFlagParam) -> None:
        """Report a question to the moderators.

        :param user: the reporter
        :param pk: question ID
        :param obj: the reason
        """
        flag_dao.create(user.sub, ContentType.QUESTION, pk, obj.reason)


question_service: QuestionService = QuestionService()
