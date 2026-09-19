"""Registration, sessions and onboarding."""

from backend.common.tables import USERS
from backend.tests.conftest import data


def test_registration_creates_both_the_auth_user_and_the_profile(client, db, seed):
    response = client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})

    assert response.status_code == 201
    user_id = data(response)['user_id']
    assert db.auth_users[user_id]['email'] == 'new@example.com'
    profile = db.find(USERS, user_id)
    assert profile['role'] == 'user'
    assert profile['onboarding_complete'] is False


def test_registration_normalises_the_address(client, db, seed):
    client.post('/api/v1/auth/register', json={'email': '  NEW@Example.COM ', 'password': 'correct horse'})

    assert db.rows(USERS)[-1]['email'] == 'new@example.com'


def test_registering_twice_is_a_conflict(client, seed):
    client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})

    response = client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})

    assert response.status_code == 409


def test_a_short_password_is_rejected(client, db, seed):
    response = client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'short'})

    assert response.status_code == 400
    assert 'password' in response.json()['data']
    assert db.auth_users == {}


def test_a_failed_profile_write_rolls_the_auth_user_back(client, db, seed, monkeypatch):
    """There is no transaction across Supabase Auth and the database.

    If the profile write fails the auth user has to be removed by hand, or the
    account can sign in with nothing behind it.
    """
    from backend.app.admin.crud import crud_user

    def boom(payload: dict) -> None:
        raise RuntimeError('profile write failed')

    monkeypatch.setattr(crud_user.user_dao, 'create_profile', staticmethod(boom))

    response = client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})

    assert response.status_code == 500
    assert db.auth_users == {}


def test_login_returns_a_session_and_the_role(client, db, seed):
    registered = data(
        client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})
    )

    response = client.post('/api/v1/auth/login', json={'email': 'new@example.com', 'password': 'correct horse'})

    assert response.status_code == 200
    session = data(response)
    assert session['access_token'] == f'access-{registered["user_id"]}'
    assert session['user']['role'] == 'user'


def test_login_with_the_wrong_password_is_401(client, seed):
    client.post('/api/v1/auth/register', json={'email': 'new@example.com', 'password': 'correct horse'})

    response = client.post('/api/v1/auth/login', json={'email': 'new@example.com', 'password': 'wrong'})

    assert response.status_code == 401


def test_password_reset_answers_the_same_for_unknown_addresses(client, db, seed):
    """The reply must not reveal who has an account."""
    known = client.post('/api/v1/auth/forgot-password', json={'email': 'user@example.com'})
    unknown = client.post('/api/v1/auth/forgot-password', json={'email': 'nobody@example.com'})

    assert known.status_code == unknown.status_code == 200
    assert known.json()['msg'] == unknown.json()['msg']
    assert db.sent_resets == ['user@example.com', 'nobody@example.com']


def test_resending_verification_answers_the_same_way(client, seed):
    known = client.post('/api/v1/auth/resend-verification', json={'email': 'user@example.com'})
    unknown = client.post('/api/v1/auth/resend-verification', json={'email': 'nobody@example.com'})

    assert known.json()['msg'] == unknown.json()['msg']


def test_logout_signs_the_token_out(as_user, db, seed):
    client = as_user(seed['user']['id'])

    assert client.post('/api/v1/auth/logout').status_code == 200
    assert db.signed_out == [f'token-{seed["user"]["id"]}']


def test_onboarding_stores_the_answers(as_user, db, seed):
    client = as_user(seed['user']['id'], email='user@example.com')

    response = client.patch(
        '/api/v1/users/onboarding',
        json={
            'domain_id': seed['domain']['id'],
            'skill_level': 'beginner',
            'goal': 'first_job',
            'university': '  NUST  ',
        },
    )

    assert response.status_code == 200
    profile = db.find(USERS, seed['user']['id'])
    assert profile['onboarding_complete'] is True
    assert profile['domain_id'] == seed['domain']['id']
    assert profile['university'] == 'NUST'


def test_onboarding_strips_markup_from_the_university(as_user, db, seed):
    client = as_user(seed['user']['id'])

    client.patch(
        '/api/v1/users/onboarding',
        json={
            'domain_id': seed['domain']['id'],
            'skill_level': 'beginner',
            'goal': 'first_job',
            'university': '<img src=x onerror=alert(1)>NUST',
        },
    )

    assert db.find(USERS, seed['user']['id'])['university'] == 'NUST'


def test_onboarding_rejects_an_unknown_goal(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.patch(
        '/api/v1/users/onboarding',
        json={
            'domain_id': seed['domain']['id'],
            'skill_level': 'beginner',
            'goal': 'world_domination',
            'university': 'NUST',
        },
    )

    assert response.status_code == 400


def test_domains_are_public_to_signed_in_users(client, seed):
    domains = data(client.get('/api/v1/domains'))

    assert [d['slug'] for d in domains] == ['software-engineering']
