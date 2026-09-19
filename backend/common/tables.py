"""Database table names.

There are no ORM models: the CRUD layer talks to PostgREST, which addresses tables
by name. Keeping the names here means a rename is one edit, and it gives the CRUD
classes something to import instead of scattering string literals.

Schema lives in supabase/migrations/; see backend/scripts/migrate.py.
"""

DOMAINS = 'domains'
USERS = 'users'
COMPANIES = 'companies'
COMPANY_ADMINS = 'company_admins'
COMPANY_EDIT_REQUESTS = 'company_edit_requests'
INTERVIEW_QUESTIONS = 'interview_questions'
INTERVIEW_REVIEWS = 'interview_reviews'
QUESTION_UPVOTES = 'question_upvotes'
CONTENT_FLAGS = 'content_flags'
APPLICATIONS = 'applications'
PREP_PROGRESS = 'prep_progress'
ADMIN_AUDIT_LOG = 'admin_audit_log'

# Tables a content flag can point at, keyed by ContentType
FLAGGABLE = {
    'question': INTERVIEW_QUESTIONS,
    'review': INTERVIEW_REVIEWS,
}
