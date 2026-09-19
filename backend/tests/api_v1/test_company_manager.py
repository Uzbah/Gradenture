"""Per-company managers and the queued profile edits they propose.

Ported from the old smoke_managers.py. The rule under test throughout: a company
manager may propose changes to its own profile and nothing else — never approve
them, never touch the questions and reviews written about the company.
"""

from backend.common.enums import UserRole
from backend.common.tables import ADMIN_AUDIT_LOG, COMPANIES, COMPANY_ADMINS, COMPANY_EDIT_REQUESTS
from backend.tests.conftest import data


def audited(db) -> list[str]:
    return [row['action'] for row in db.rows(ADMIN_AUDIT_LOG)]


def make_manager(db, seed) -> dict:
    return db.seed(
        COMPANY_ADMINS,
        {
            'company_id': seed['company']['id'],
            'user_id': seed['user']['id'],
            'granted_by': seed['admin']['id'],
        },
    )


# --- granting and revoking ---


def test_a_plain_user_cannot_grant_manager_rights(as_user, db, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/managers',
        json={'email': 'user@example.com'},
    )

    assert response.status_code == 403
    assert db.rows(COMPANY_ADMINS) == []


def test_admin_grants_manager_rights(as_user, db, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/managers',
        json={'email': 'user@example.com'},
    )

    assert response.status_code == 201
    assert db.rows(COMPANY_ADMINS)[0]['user_id'] == seed['user']['id']
    assert 'company_manager_granted' in audited(db)


def test_granting_to_an_unknown_email_is_404(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/managers',
        json={'email': 'nobody@example.com'},
    )

    assert response.status_code == 404


def test_granting_to_a_malformed_email_is_rejected_before_the_lookup(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/managers',
        json={'email': 'not-an-address'},
    )

    assert response.status_code == 400
    assert 'email' in response.json()['data']


def test_a_duplicate_grant_is_rejected(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.post(
        f'/api/v1/admin/companies/{seed["company"]["id"]}/managers',
        json={'email': 'user@example.com'},
    )

    assert response.status_code == 409
    assert len(db.rows(COMPANY_ADMINS)) == 1


def test_managers_are_listed(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    managers = data(client.get(f'/api/v1/admin/companies/{seed["company"]["id"]}/managers'))

    assert [m['user_id'] for m in managers] == [seed['user']['id']]


def test_a_manager_sees_the_company_under_managed(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    companies = data(client.get('/api/v1/companies/managed'))

    assert [c['id'] for c in companies] == [seed['company']['id']]


def test_revoking_removes_the_grant(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.delete(f'/api/v1/admin/companies/{seed["company"]["id"]}/managers/{seed["user"]["id"]}')

    assert response.status_code == 200
    assert db.rows(COMPANY_ADMINS) == []
    assert 'company_manager_revoked' in audited(db)


def test_revoking_a_non_manager_is_404(as_user, seed):
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.delete(f'/api/v1/admin/companies/{seed["company"]["id"]}/managers/{seed["user"]["id"]}')

    assert response.status_code == 404


# --- proposing edits ---


def test_a_non_manager_cannot_propose_an_edit(as_user, db, seed):
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post(f'/api/v1/companies/{seed["company"]["id"]}/edit-request', json={'industry': 'Sneaky'})

    assert response.status_code == 403
    assert db.rows(COMPANY_EDIT_REQUESTS) == []


def test_a_managers_edit_is_queued_not_applied(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post(
        f'/api/v1/companies/{seed["company"]["id"]}/edit-request',
        json={'industry': 'Fintech', 'website': 'https://mgr.example'},
    )

    assert response.status_code == 201
    assert data(response)['status'] == 'pending'
    # Nothing a company writes about itself goes live unreviewed.
    assert db.find(COMPANIES, seed['company']['id']).get('industry') is None


def test_a_second_pending_edit_is_rejected(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    client.post(f'/api/v1/companies/{seed["company"]["id"]}/edit-request', json={'industry': 'Fintech'})
    response = client.post(f'/api/v1/companies/{seed["company"]["id"]}/edit-request', json={'industry': 'Again'})

    assert response.status_code == 409
    assert len(db.rows(COMPANY_EDIT_REQUESTS)) == 1


def test_an_empty_edit_is_rejected(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.post(f'/api/v1/companies/{seed["company"]["id"]}/edit-request', json={})

    assert response.status_code == 400
    assert db.rows(COMPANY_EDIT_REQUESTS) == []


def test_a_manager_cannot_set_the_registry_status(as_user, db, seed):
    make_manager(db, seed)
    client = as_user(seed['user']['id'], UserRole.USER)

    client.post(
        f'/api/v1/companies/{seed["company"]["id"]}/edit-request',
        json={'industry': 'Fintech', 'status': 'approved'},
    )

    # `status` is not a field of the edit schema, so it is dropped rather than queued.
    assert 'status' not in db.rows(COMPANY_EDIT_REQUESTS)[0]['changes']


# --- deciding edits ---


def test_a_manager_cannot_approve_their_own_edit(as_user, db, seed):
    make_manager(db, seed)
    request = db.seed(
        COMPANY_EDIT_REQUESTS,
        {
            'company_id': seed['company']['id'],
            'requested_by': seed['user']['id'],
            'changes': {'industry': 'Fintech'},
            'status': 'pending',
        },
    )
    client = as_user(seed['user']['id'], UserRole.USER)

    response = client.patch(f'/api/v1/admin/company-edits/{request["id"]}', json={'status': 'approved'})

    assert response.status_code == 403
    assert db.find(COMPANY_EDIT_REQUESTS, request['id'])['status'] == 'pending'


def test_approving_an_edit_applies_it_and_clears_the_queue(as_user, db, seed):
    request = db.seed(
        COMPANY_EDIT_REQUESTS,
        {
            'company_id': seed['company']['id'],
            'requested_by': seed['user']['id'],
            'changes': {'industry': 'Fintech', 'name': '  Acme Fintech '},
            'status': 'pending',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    assert client.patch(f'/api/v1/admin/company-edits/{request["id"]}', json={'status': 'approved'}).status_code == 200

    company = db.find(COMPANIES, seed['company']['id'])
    assert company['industry'] == 'Fintech'
    # The name is trimmed and the slug regenerated, as on any other rename.
    assert company['name'] == 'Acme Fintech'
    assert company['slug'] == 'acme-fintech'

    assert data(client.get('/api/v1/admin/company-edits')) == []
    assert 'company_edit_approved' in audited(db)


def test_rejecting_an_edit_leaves_the_company_alone(as_user, db, seed):
    request = db.seed(
        COMPANY_EDIT_REQUESTS,
        {
            'company_id': seed['company']['id'],
            'requested_by': seed['user']['id'],
            'changes': {'industry': 'Not accurate'},
            'status': 'pending',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(
        f'/api/v1/admin/company-edits/{request["id"]}',
        json={'status': 'rejected', 'admin_note': 'not accurate'},
    )

    assert response.status_code == 200
    assert db.find(COMPANIES, seed['company']['id']).get('industry') is None
    assert db.find(COMPANY_EDIT_REQUESTS, request['id'])['status'] == 'rejected'
    assert 'company_edit_rejected' in audited(db)


def test_deciding_an_already_closed_edit_is_404(as_user, db, seed):
    request = db.seed(
        COMPANY_EDIT_REQUESTS,
        {
            'company_id': seed['company']['id'],
            'requested_by': seed['user']['id'],
            'changes': {'industry': 'Fintech'},
            'status': 'approved',
        },
    )
    client = as_user(seed['admin']['id'], UserRole.ADMIN)

    response = client.patch(f'/api/v1/admin/company-edits/{request["id"]}', json={'status': 'approved'})

    assert response.status_code == 404


def test_a_revoked_manager_can_no_longer_propose_edits(as_user, db, seed):
    make_manager(db, seed)
    admin_client = as_user(seed['admin']['id'], UserRole.ADMIN)
    admin_client.delete(f'/api/v1/admin/companies/{seed["company"]["id"]}/managers/{seed["user"]["id"]}')

    client = as_user(seed['user']['id'], UserRole.USER)
    response = client.post(f'/api/v1/companies/{seed["company"]["id"]}/edit-request', json={'industry': 'After revoke'})

    assert response.status_code == 403
