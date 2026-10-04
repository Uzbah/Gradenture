"""The response envelope and the error handlers, which every endpoint shares."""

from backend.tests.conftest import data


def test_a_successful_response_carries_code_msg_and_data(client, seed):
    response = client.get('/api/v1/questions/')

    body = response.json()
    assert body['code'] == 200
    assert body['msg'] == 'Success'
    assert set(data(response)) == {'items', 'total', 'page', 'size', 'total_pages'}


def test_a_not_found_uses_the_same_envelope(client, seed):
    response = client.get('/api/v1/questions/00000000-0000-0000-0000-000000000000')

    assert response.status_code == 404
    assert response.json() == {'code': 404, 'msg': 'Question not found', 'data': None}


def test_an_unknown_path_uses_the_same_envelope(client):
    response = client.get('/api/v1/nope')

    assert response.status_code == 404
    assert response.json()['code'] == 404


def test_validation_errors_report_per_field(as_user, seed):
    client = as_user(seed['user']['id'])

    response = client.post('/api/v1/questions/', json={'domain_id': seed['domain']['id']})

    assert response.status_code == 400
    body = response.json()
    assert body['code'] == 422
    # The frontend renders this map directly, so its shape is part of the contract.
    assert body['data']['company_id'] == ['Field required']


def test_a_missing_token_is_reported_as_unauthenticated(client):
    response = client.get('/api/v1/users/me')

    assert response.status_code == 401
    assert response.json()['msg'] == 'Not authenticated'


def test_every_response_carries_a_request_id(client, seed):
    response = client.get('/api/v1/questions/')

    assert response.headers['X-Request-ID']


def test_an_inbound_request_id_is_reused(client, seed):
    response = client.get('/api/v1/questions/', headers={'X-Request-ID': 'abc123'})

    assert response.headers['X-Request-ID'] == 'abc123'


def test_the_api_root_still_answers(client):
    body = client.get('/api/v1').json()

    assert body['docs'] == '/docs'
