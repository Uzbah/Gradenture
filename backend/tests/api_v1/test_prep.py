"""Prep roadmaps and the preparedness score."""

from backend.common.tables import PREP_PROGRESS, USERS
from backend.tests.conftest import data


def onboarded(db, seed) -> dict:
    """Put the seeded user on the software-engineering roadmap."""
    user = next(u for u in db.store[USERS] if u['id'] == seed['user']['id'])
    user['domain_id'] = seed['domain']['id']
    return seed


def test_the_roadmap_starts_empty_with_a_zero_score(as_user, db, seed):
    onboarded(db, seed)
    client = as_user(seed['user']['id'])

    prep = data(client.get('/api/v1/prep/'))

    assert prep['score'] == 0
    assert len(prep['topics']) == 8
    assert all(topic['completed'] is False for topic in prep['topics'])


def test_completing_a_topic_moves_the_score(as_user, db, seed):
    onboarded(db, seed)
    client = as_user(seed['user']['id'])

    prep = data(client.patch('/api/v1/prep/', json={'topic': 'Databases & SQL', 'completed': True}))

    # 1 of 8 is 12.5%; round() breaks the tie to even, as it did before the move.
    assert prep['score'] == 12
    assert next(t for t in prep['topics'] if t['topic'] == 'Databases & SQL')['completed'] is True


def test_a_topic_can_be_unmarked(as_user, db, seed):
    onboarded(db, seed)
    client = as_user(seed['user']['id'])

    client.patch('/api/v1/prep/', json={'topic': 'Databases & SQL', 'completed': True})
    prep = data(client.patch('/api/v1/prep/', json={'topic': 'Databases & SQL', 'completed': False}))

    assert prep['score'] == 0
    # Toggling twice updates the row rather than inserting a second one.
    assert len(db.rows(PREP_PROGRESS)) == 1


def test_a_topic_outside_the_roadmap_is_rejected(as_user, db, seed):
    onboarded(db, seed)
    client = as_user(seed['user']['id'])

    response = client.patch('/api/v1/prep/', json={'topic': 'Underwater Basket Weaving', 'completed': True})

    assert response.status_code == 400
    assert db.rows(PREP_PROGRESS) == []


def test_prep_needs_onboarding_first(as_user, db, seed):
    client = as_user(seed['user']['id'])

    response = client.get('/api/v1/prep/')

    assert response.status_code == 400
    assert response.json()['msg'] == 'Complete onboarding first'
