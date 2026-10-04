"""Company administration: creation, edits, the public/admin split, and merges.

Ported from the old smoke_companies.py.
"""

from backend.common.enums import UserRole
from backend.common.tables import ADMIN_AUDIT_LOG, COMPANIES, INTERVIEW_QUESTIONS
from backend.tests.conftest import data


def audited(db) -> list[str]:
    return [row['action'] for row in db.rows(ADMIN_AUDIT_LOG)]


def test_admin_creates_an_already_approved_company(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        '/api/v1/admin/companies',
        json={'name': 'ZZ Keep', 'website': 'https://keep.example', 'industry': 'Software'},
    )

    assert response.status_code == 201
    company = data(response)
    # Admin-created companies skip the queue.
    assert company['status'] == 'approved'
    assert company['slug'] == 'zz-keep'
    assert 'company_created' in audited(db)


def test_a_plain_user_cannot_create_a_company_directly(as_user, db, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    assert client.post('/api/v1/admin/companies', json={'name': 'Nope'}).status_code == 403
    assert len(db.rows(COMPANIES)) == 1


def test_a_duplicate_name_is_rejected(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post('/api/v1/admin/companies', json={'name': 'acme'})

    assert response.status_code == 409


def test_editing_leaves_untouched_fields_alone(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    company = data(
        client.patch(
            f'/api/v1/admin/companies/{seed["company"]["id"]}',
            json={'industry': 'Fintech', 'logo_url': 'https://a.example/logo.png'},
        )
    )

    assert company['industry'] == 'Fintech'
    assert company['website'] == 'https://acme.example'


def test_renaming_regenerates_the_slug(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    company = data(client.patch(f'/api/v1/admin/companies/{seed["company"]["id"]}', json={'name': 'Acme Renamed'}))

    assert company['slug'] == 'acme-renamed'


def test_an_empty_patch_approves_a_pending_company(as_user, db, seed):
    pending = db.seed(COMPANIES, {'name': 'Pending Co', 'slug': 'pending-co', 'status': 'pending'})
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.patch(f'/api/v1/admin/companies/{pending["id"]}').status_code == 200
    assert db.find(COMPANIES, pending['id'])['status'] == 'approved'
    assert 'company_approved' in audited(db)


def test_editing_an_unknown_company_is_404(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch('/api/v1/admin/companies/00000000-0000-0000-0000-000000000000', json={'industry': 'X'})

    assert response.status_code == 404


def test_the_admin_list_shows_pending_but_the_public_one_does_not(as_user, client, db, seed):
    pending = db.seed(COMPANIES, {'name': 'Pending Co', 'slug': 'pending-co', 'status': 'pending'})

    public = data(client.get('/api/v1/companies/'))
    assert pending['id'] not in [c['id'] for c in public['items']]

    admin_client = as_user(seed['admin']['id'], UserRole.ADMIN)
    admin_list = data(admin_client.get('/api/v1/admin/companies'))
    assert pending['id'] in [c['id'] for c in admin_list['items']]


# --- merging ---


def test_merging_moves_content_and_removes_the_duplicate(as_user, db, seed):
    duplicate = db.seed(COMPANIES, {'name': 'Acme Dupe', 'slug': 'acme-dupe', 'status': 'approved'})
    question = db.seed(
        INTERVIEW_QUESTIONS,
        {
            'submitted_by': seed['user']['id'],
            'domain_id': seed['domain']['id'],
            'company_id': duplicate['id'],
            'role_title': 'Software Engineer',
            'question_text': 'Explain the CAP theorem in your own words',
            'question_type': 'technical',
            'difficulty': 'medium',
            'asked_date': '2026-01-01',
            'status': 'approved',
            'upvotes': 0,
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(f'/api/v1/admin/companies/{duplicate["id"]}/merge', json={'into_id': seed['company']['id']})

    assert response.status_code == 200
    assert data(response)['interview_questions'] == 1
    assert response.json()['msg'] == 'Merged Acme Dupe into Acme'
    assert db.find(INTERVIEW_QUESTIONS, question['id'])['company_id'] == seed['company']['id']
    assert db.find(COMPANIES, duplicate['id']) is None
    assert 'company_merged' in audited(db)


def test_merging_a_company_into_itself_is_rejected(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/merge',
        json={'into_id': seed['company']['id']},
    )

    assert response.status_code == 400
    assert db.find(COMPANIES, seed['company']['id']) is not None


def test_merging_an_unknown_company_is_404(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        '/api/v1/admin/companies/00000000-0000-0000-0000-000000000000/merge',
        json={'into_id': seed['company']['id']},
    )

    assert response.status_code == 404


# --- user submissions ---


def test_a_user_submission_enters_the_queue_as_pending(as_user, db, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post('/api/v1/companies/', json={'name': 'Brand New Co'})

    assert response.status_code == 201
    assert data(response)['status'] == 'pending'
    submitted = next(c for c in db.rows(COMPANIES) if c['name'] == 'Brand New Co')
    assert submitted['status'] == 'pending'
    assert submitted['slug'] == 'brand-new-co'


def test_a_user_cannot_submit_a_duplicate(as_user, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    assert client.post('/api/v1/companies/', json={'name': 'ACME'}).status_code == 409
