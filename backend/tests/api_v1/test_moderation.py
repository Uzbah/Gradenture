"""Moderation, flags and user administration.

Ported from the old smoke_admin.py, which needed a live server, a real Supabase
project and a super admin already in the database.
"""

from backend.common.enums import UserRole
from backend.common.tables import ADMIN_AUDIT_LOG, CONTENT_FLAGS, INTERVIEW_QUESTIONS, USERS
from backend.tests.conftest import data


def audited(db) -> list[str]:
    return [row['action'] for row in db.rows(ADMIN_AUDIT_LOG)]


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
            'status': 'pending',
            'upvotes': 0,
            **overrides,
        },
    )


# --- role gating ---


def test_plain_user_is_refused_the_queue(as_user, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    assert client.get('/api/v1/admin/queue').status_code == 403


def test_admin_reaches_the_queue(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.get('/api/v1/admin/queue').status_code == 200


def test_anonymous_caller_is_refused(client):
    assert client.get('/api/v1/admin/queue').status_code == 401


# --- the queue ---


def test_queue_lists_everything_awaiting_review(as_user, db, seed):
    question = make_question(db, seed)
    company = db.seed('companies', {'name': 'Pending Co', 'slug': 'pending-co', 'status': 'pending'})
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    queue = data(client.get('/api/v1/admin/queue'))

    assert [q['id'] for q in queue['questions']] == [question['id']]
    assert [c['id'] for c in queue['companies']] == [company['id']]


def test_approved_content_leaves_the_queue(as_user, db, seed):
    make_question(db, seed, status='approved')
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert data(client.get('/api/v1/admin/queue'))['questions'] == []


# --- decisions ---


def test_approving_a_question_publishes_it_and_is_audited(as_user, db, seed):
    question = make_question(db, seed)
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(
        f'/api/v1/admin/questions/{question["id"]}',
        json={'status': 'approved', 'admin_note': 'clear and useful'},
    )

    assert response.status_code == 200
    stored = db.find(INTERVIEW_QUESTIONS, question['id'])
    assert stored['status'] == 'approved'
    assert stored['reviewed_by'] == seed['admin']['id']
    assert stored['admin_note'] == 'clear and useful'
    assert 'question_approved' in audited(db)


def test_moderating_an_unknown_question_is_404(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(
        '/api/v1/admin/questions/00000000-0000-0000-0000-000000000000',
        json={'status': 'approved'},
    )

    assert response.status_code == 404


def test_an_invalid_decision_is_rejected(as_user, db, seed):
    question = make_question(db, seed)
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(f'/api/v1/admin/questions/{question["id"]}', json={'status': 'deleted'})

    assert response.status_code == 400
    assert db.find(INTERVIEW_QUESTIONS, question['id'])['status'] == 'pending'


# --- flags ---


def test_open_flags_are_listed_with_their_content(as_user, db, seed):
    question = make_question(db, seed)
    flag = db.seed(
        CONTENT_FLAGS,
        {
            'reported_by': seed['user']['id'],
            'content_type': 'question',
            'content_id': question['id'],
            'reason': 'off topic',
            'status': 'open',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    flags = data(client.get('/api/v1/admin/flags'))

    assert [f['id'] for f in flags] == [flag['id']]
    assert flags[0]['content']['id'] == question['id']


def test_a_flag_on_deleted_content_degrades_gracefully(as_user, db, seed):
    db.seed(
        CONTENT_FLAGS,
        {
            'reported_by': seed['user']['id'],
            'content_type': 'question',
            'content_id': '00000000-0000-0000-0000-000000000000',
            'reason': 'gone',
            'status': 'open',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert data(client.get('/api/v1/admin/flags'))[0]['content'] is None


def test_a_flag_can_be_dismissed_once(as_user, db, seed):
    flag = db.seed(
        CONTENT_FLAGS,
        {
            'reported_by': seed['user']['id'],
            'content_type': 'question',
            'content_id': '00000000-0000-0000-0000-000000000000',
            'reason': 'noise',
            'status': 'open',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.patch(f'/api/v1/admin/flags/{flag["id"]}', json={'status': 'dismissed'}).status_code == 200
    # Closing it again must not write a second audit row.
    assert client.patch(f'/api/v1/admin/flags/{flag["id"]}', json={'status': 'dismissed'}).status_code == 404
    assert audited(db).count('flag_dismissed') == 1


# --- self-action guards and suspension ---


def test_a_super_admin_cannot_demote_themselves(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.SUPER_ADMIN)

    response = client.patch(f'/api/v1/admin/users/{seed["admin"]["id"]}/role', json={'role': 'user'})

    assert response.status_code == 400
    assert db.find(USERS, seed['admin']['id'])['role'] == 'super_admin'


def test_an_admin_cannot_suspend_themselves(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.patch(f'/api/v1/admin/users/{seed["admin"]["id"]}/suspend').status_code == 400


def test_suspend_and_unsuspend_round_trip(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)
    target = seed['user']['id']

    assert client.patch(f'/api/v1/admin/users/{target}/suspend').status_code == 200
    assert db.find(USERS, target)['suspended_at'] is not None
    assert db.auth_users.setdefault(target, {}).get('banned_until') is not None

    assert client.patch(f'/api/v1/admin/users/{target}/unsuspend').status_code == 200
    assert db.find(USERS, target)['suspended_at'] is None
    assert db.auth_users[target]['banned_until'] is None

    assert 'user_suspended' in audited(db)
    assert 'user_unsuspended' in audited(db)


def test_role_changes_are_written_to_both_copies(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.SUPER_ADMIN)
    target = seed['user']['id']

    assert client.patch(f'/api/v1/admin/users/{target}/role', json={'role': 'admin'}).status_code == 200

    assert db.find(USERS, target)['role'] == 'admin'
    assert db.auth_users[target]['user_metadata'] == {'role': 'admin'}
    assert 'role_updated' in audited(db)


def test_only_a_super_admin_changes_roles(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(f'/api/v1/admin/users/{seed["user"]["id"]}/role', json={'role': 'admin'})

    assert response.status_code == 403
    assert db.find(USERS, seed['user']['id'])['role'] == 'user'


def test_warning_a_user_is_recorded(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.patch(f'/api/v1/admin/users/{seed["user"]["id"]}/warn').status_code == 200
    assert 'user_warned' in audited(db)
