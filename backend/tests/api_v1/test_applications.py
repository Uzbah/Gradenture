"""The application tracker, which is private to each user.

The service role bypasses row level security, so the isolation these tests check
is enforced entirely by the query scoping in crud_application.py. A leak here
would be silent in production.
"""

from backend.common.enums import UserRole
from backend.common.tables import APPLICATIONS
from backend.tests.conftest import data

OTHER_USER = '99999999-9999-9999-9999-999999999999'


def make_application(db, user_id, **overrides) -> dict:
    return db.seed(
        APPLICATIONS,
        {
            'user_id': user_id,
            'company_name': 'Acme',
            'role_title': 'Software Engineer',
            'status': 'applied',
            **overrides,
        },
    )


def test_the_list_shows_only_the_callers_rows(as_user, db, seed):
    mine = make_application(db, seed['user']['id'])
    make_application(db, OTHER_USER)
    client = as_user(seed['user']['id'])

    page = data(client.get('/api/v1/applications/'))

    assert [a['id'] for a in page['items']] == [mine['id']]
    assert page['total'] == 1


def test_the_list_can_be_filtered_by_column(as_user, db, seed):
    make_application(db, seed['user']['id'], status='applied')
    offer = make_application(db, seed['user']['id'], status='offer')
    client = as_user(seed['user']['id'])

    page = data(client.get('/api/v1/applications/?status=offer'))

    assert [a['id'] for a in page['items']] == [offer['id']]


def test_someone_elses_application_is_not_found(as_user, db, seed):
    theirs = make_application(db, OTHER_USER)
    client = as_user(seed['user']['id'])

    # 404 rather than 403: the tracker should not confirm the row exists.
    assert client.get(f'/api/v1/applications/{theirs["id"]}').status_code == 404


def test_someone_elses_application_cannot_be_updated(as_user, db, seed):
    theirs = make_application(db, OTHER_USER)
    client = as_user(seed['user']['id'])

    response = client.patch(f'/api/v1/applications/{theirs["id"]}', json={'status': 'offer'})

    assert response.status_code == 404
    assert db.find(APPLICATIONS, theirs['id'])['status'] == 'applied'


def test_someone_elses_application_cannot_be_deleted(as_user, db, seed):
    theirs = make_application(db, OTHER_USER)
    client = as_user(seed['user']['id'])

    assert client.delete(f'/api/v1/applications/{theirs["id"]}').status_code == 404
    assert db.find(APPLICATIONS, theirs['id']) is not None


def test_creating_an_application_assigns_it_to_the_caller(as_user, db, seed):
    client = as_user(seed['user']['id'])

    response = client.post(
        '/api/v1/applications/',
        json={'company_name': '  Acme  ', 'role_title': 'Engineer', 'status': 'interview'},
    )

    assert response.status_code == 201
    created = data(response)
    assert created['user_id'] == seed['user']['id']
    # Whitespace is trimmed by the schema.
    assert created['company_name'] == 'Acme'


def test_creating_an_application_strips_html_from_notes(as_user, db, seed):
    client = as_user(seed['user']['id'])

    client.post(
        '/api/v1/applications/',
        json={'company_name': 'Acme', 'role_title': 'Engineer', 'notes': '<b>referral</b>'},
    )

    assert db.rows(APPLICATIONS)[0]['notes'] == 'referral'


def test_an_empty_company_name_is_rejected(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.post('/api/v1/applications/', json={'company_name': '   ', 'role_title': 'Engineer'})

    assert response.status_code == 400
    assert 'company_name' in response.json()['data']


def test_an_invalid_status_is_rejected(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.post(
        '/api/v1/applications/',
        json={'company_name': 'Acme', 'role_title': 'Engineer', 'status': 'ghosted'},
    )

    assert response.status_code == 400


def test_updating_leaves_omitted_fields_alone(as_user, db, seed):
    mine = make_application(db, seed['user']['id'], notes='keep me')
    client = as_user(seed['user']['id'])

    updated = data(client.patch(f'/api/v1/applications/{mine["id"]}', json={'status': 'offer'}))

    assert updated['status'] == 'offer'
    assert updated['notes'] == 'keep me'


def test_deleting_removes_the_row(as_user, db, seed):
    mine = make_application(db, seed['user']['id'])
    client = as_user(seed['user']['id'], UserRole.USER)

    assert client.delete(f'/api/v1/applications/{mine["id"]}').status_code == 200
    assert db.rows(APPLICATIONS) == []


def test_the_tracker_requires_authentication(client):
    assert client.get('/api/v1/applications/').status_code == 401
