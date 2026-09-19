from backend.app.career.crud.crud_prep import prep_dao
from backend.common.dataclasses import CurrentUser
from backend.common.exception import errors

# ponytail: static topic lists keyed by domain slug; move to an admin-curated
# roadmaps table when admins need to edit content without a deploy
TOPICS: dict[str, list[str]] = {
    'software-engineering': [
        'Data Structures & Algorithms',
        'System Design Basics',
        'Databases & SQL',
        'REST APIs & HTTP',
        'Git & Version Control',
        'Testing & Debugging',
        'OOP & Design Patterns',
        'Behavioural / STAR Method',
    ],
    'data-science-ai': [
        'Statistics & Probability',
        'Python & Pandas',
        'SQL for Analytics',
        'Machine Learning Fundamentals',
        'Model Evaluation & Metrics',
        'Deep Learning Basics',
        'Data Storytelling & Visualization',
        'Behavioural / STAR Method',
    ],
    'finance-banking': [
        'Financial Statements',
        'Valuation Methods',
        'Excel & Financial Modeling',
        'Market & Economic Awareness',
        'Accounting Fundamentals',
        'Risk & Compliance Basics',
        'Behavioural / STAR Method',
    ],
    'marketing-sales': [
        'Marketing Fundamentals & 4Ps',
        'Digital Marketing Channels',
        'Analytics & KPIs',
        'Copywriting & Communication',
        'CRM & Sales Process',
        'Case Study Practice',
        'Behavioural / STAR Method',
    ],
    'product-management': [
        'Product Sense & Design Questions',
        'Metrics & Analytics',
        'Prioritization Frameworks',
        'Technical Fluency Basics',
        'Market & User Research',
        'Case Study Practice',
        'Behavioural / STAR Method',
    ],
    'human-resources': [
        'Recruitment & Selection',
        'Employment Law Basics',
        'Performance Management',
        'Compensation & Benefits',
        'HR Analytics',
        'Conflict Resolution',
        'Behavioural / STAR Method',
    ],
    'accounting': [
        'Journal Entries & Ledgers',
        'Financial Statements',
        'IFRS / GAAP Basics',
        'Taxation Fundamentals',
        'Auditing Basics',
        'Excel Skills',
        'Behavioural / STAR Method',
    ],
    'consulting': [
        'Case Interview Frameworks',
        'Market Sizing / Guesstimates',
        'Profitability Cases',
        'Mental Math & Charts',
        'Structured Communication',
        'Industry Awareness',
        'Behavioural / STAR Method',
    ],
}


class PrepService:
    """Interview-preparation roadmaps and the preparedness score."""

    @staticmethod
    def _user_domain(user_id: str) -> tuple[str, str]:
        """The caller's domain id and slug.

        The roadmap is chosen by domain, so a user who has not finished onboarding
        has no roadmap to show.
        """
        row = prep_dao.get_user_domain(user_id)
        if not row or not row.get('domain_id'):
            raise errors.RequestError(msg='Complete onboarding first')
        return row['domain_id'], row['domains']['slug']

    @staticmethod
    def get(*, user: CurrentUser) -> dict:
        """The caller's roadmap, with each topic's state and the overall score.

        :param user: the caller
        """
        domain_id, slug = PrepService._user_domain(user.sub)
        topics = TOPICS.get(slug, [])

        done = {row['topic'] for row in prep_dao.get_progress(user.sub, domain_id) if row['completed']}
        topic_list = [{'topic': topic, 'completed': topic in done} for topic in topics]
        completed = sum(1 for topic in topic_list if topic['completed'])

        return {
            'domain_id': domain_id,
            'topics': topic_list,
            'score': round(100 * completed / len(topics)) if topics else 0,
        }

    @staticmethod
    def toggle_topic(*, user: CurrentUser, topic: str, completed: bool) -> dict:
        """Mark a topic done or not done, and return the updated roadmap.

        :param user: the caller
        :param topic: topic name, which must be on the caller's roadmap
        :param completed: new state
        """
        domain_id, slug = PrepService._user_domain(user.sub)
        if topic not in TOPICS.get(slug, []):
            raise errors.RequestError(msg='Unknown topic for your domain')

        prep_dao.set_topic(user.sub, domain_id, topic, completed)
        return PrepService.get(user=user)


prep_service: PrepService = PrepService()
