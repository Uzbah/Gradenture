"""Questions: browsing, submission, upvotes and flags."""

from backend.common.enums import UserRole
from backend.common.tables import CONTENT_FLAGS, INTERVIEW_QUESTIONS
from backend.tests.conftest import data


def make_question(db, seed, **overrides) -> dict:
    return db.seed(
        INTERVIEW_QUESTIONS,
        {
            'submitted_by': seed['user']['id'],
            'domain_id': seed['domain']['id'],
            'company_id': seed['company']['id'],
            'role_title': 'Software Engineer',
            'question_text': 'Explain the CAP theorem in your own words',
            'question_type': 'technical',
            'difficulty': 'medium',
            'asked_date': '2026-01-01',
            'is_anonymous': False,
            'status': 'approved',
            'upvotes': 0,
            **overrides,
        },
    )


def test_list_returns_only_approved_questions(client, db, seed):
    approved = make_question(db, seed)
    make_question(db, seed, status='pending')

    page = data(client.get('/api/v1/questions/'))

    assert [q['id'] for q in page['items']] == [approved['id']]
    assert page['total'] == 1


def test_list_pages_and_reports_the_total(client, db, seed):
    for _ in range(5):
        make_question(db, seed)

    page = data(client.get('/api/v1/questions/?page=2&size=2'))

    assert len(page['items']) == 2
    assert page['total'] == 5
    assert page['total_pages'] == 3
    assert page['page'] == 2


def test_list_filters_by_company(client, db, seed):
    wanted = make_question(db, seed)
    other = db.seed('companies', {'name': 'Other', 'slug': 'other', 'status': 'approved'})
    make_question(db, seed, company_id=other['id'])

    page = data(client.get(f'/api/v1/questions/?company_id={seed["company"]["id"]}'))

    assert [q['id'] for q in page['items']] == [wanted['id']]


def test_size_beyond_the_maximum_is_rejected(client, seed):
    response = client.get('/api/v1/questions/?size=999')

    assert response.status_code == 400
    assert response.json()['data'] == {'size': ['Input should be less than or equal to 50']}


def test_anonymous_submissions_hide_their_author(client, db, seed):
    question = make_question(db, seed, is_anonymous=True)

    page = data(client.get('/api/v1/questions/'))

    assert page['items'][0]['submitted_by'] is None
    # The author is still stored — moderators need to know who wrote it.
    assert db.find('interview_questions', question['id'])['submitted_by'] == seed['user']['id']


def test_get_unknown_question_is_404(client, seed):
    response = client.get('/api/v1/questions/00000000-0000-0000-0000-000000000000')

    assert response.status_code == 404
    assert response.json()['msg'] == 'Question not found'


def test_pending_questions_are_not_readable(client, db, seed):
    pending = make_question(db, seed, status='pending')

    assert client.get(f'/api/v1/questions/{pending["id"]}').status_code == 404


def test_submission_enters_the_queue_as_pending(as_user, db, seed):
    client = as_user(seed['user']['id'])

    response = client.post(
        '/api/v1/questions/',
        json={
            'domain_id': seed['domain']['id'],
            'company_id': seed['company']['id'],
            'role_title': 'Software Engineer',
            'question_text': 'What happens when you type a URL into a browser',
            'question_type': 'technical',
            'difficulty': 'medium',
            'asked_date': '2026-01-01',
        },
    )

    assert response.status_code == 201
    assert data(response)['status'] == 'pending'
    assert db.rows(INTERVIEW_QUESTIONS)[0]['submitted_by'] == seed['user']['id']


def test_submission_strips_html_from_the_question(as_user, db, seed):
    client = as_user(seed['user']['id'])

    client.post(
        '/api/v1/questions/',
        json={
            'domain_id': seed['domain']['id'],
            'company_id': seed['company']['id'],
            'role_title': 'Software Engineer',
            'question_text': '<script>alert(1)</script>Describe a hard bug you fixed',
            'question_type': 'technical',
            'difficulty': 'medium',
            'asked_date': '2026-01-01',
        },
    )

    assert '<script>' not in db.rows(INTERVIEW_QUESTIONS)[0]['question_text']


def test_submission_rejects_a_short_question(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.post(
        '/api/v1/questions/',
        json={
            'domain_id': seed['domain']['id'],
            'company_id': seed['company']['id'],
            'role_title': 'Software Engineer',
            'question_text': 'too short',
            'question_type': 'technical',
            'difficulty': 'medium',
            'asked_date': '2026-01-01',
        },
    )

    assert response.status_code == 400
    assert 'question_text' in response.json()['data']


def test_submission_requires_authentication(client, seed):
    response = client.post('/api/v1/questions/', json={})

    assert response.status_code == 401


def test_upvote_toggles_and_keeps_the_counter_in_step(as_user, db, seed):
    question = make_question(db, seed)
    client = as_user(seed['user']['id'])

    first = data(client.post(f'/api/v1/questions/{question["id"]}/upvote'))
    assert first == {'upvoted': True, 'upvotes': 1}

    second = data(client.post(f'/api/v1/questions/{question["id"]}/upvote'))
    assert second == {'upvoted': False, 'upvotes': 0}

    assert db.rows('question_upvotes') == []


def test_upvoting_an_unknown_question_is_404(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.post('/api/v1/questions/00000000-0000-0000-0000-000000000000/upvote')

    assert response.status_code == 404


def test_flagging_records_the_report(as_user, db, seed):
    question = make_question(db, seed)
    client = as_user(seed['user']['id'])

    response = client.post(f'/api/v1/questions/{question["id"]}/flag', json={'reason': 'off topic'})

    assert response.status_code == 201
    flag = db.rows(CONTENT_FLAGS)[0]
    assert flag['content_type'] == 'question'
    assert flag['content_id'] == question['id']
    assert flag['reported_by'] == seed['user']['id']


def test_flagging_rejects_a_thin_reason(as_user, db, seed):
    question = make_question(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post(f'/api/v1/questions/{question["id"]}/flag', json={'reason': 'no'})

    assert response.status_code == 400
    assert db.rows(CONTENT_FLAGS) == []
