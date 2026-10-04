"""Shared fixtures.

Every test runs against the real app object over httpx's ASGI transport: no
server, no network, no Supabase project. The data layer is the in-memory fake in
fake_supabase.py, and authentication is supplied by overriding the dependency
rather than by minting tokens.
"""

import os

import pytest

# Settings are read at import time, so these have to be set before anything
# under backend/ is imported.
os.environ.setdefault('ENVIRONMENT', 'dev')
os.environ.setdefault('SUPABASE_URL', 'https://example.supabase.co')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test-service-role-key')
os.environ.setdefault('SUPABASE_JWT_SECRET', 'test-jwt-secret')
os.environ.setdefault('RATE_LIMIT_ENABLED', 'false')
os.environ.setdefault('LOG_LEVEL', 'WARNING')

from fastapi.testclient import TestClient  # noqa: E402

from backend.common.dataclasses import CurrentUser  # noqa: E402
from backend.common.enums import UserRole  # noqa: E402
from backend.common.security.jwt import get_current_user  # noqa: E402
from backend.common.tables import DOMAINS, USERS  # noqa: E402
from backend.tests.fake_supabase import FakeSupabase  # noqa: E402

# Modules that hold a direct reference to the supabase client, which the fake
# has to replace. Missing one here shows up as a test hitting the network.
SUPABASE_CONSUMERS = (
    'backend.database.supabase',
    'backend.app.admin.crud.crud_user',
    'backend.app.admin.crud.crud_flag',
    'backend.app.admin.crud.crud_audit',
    'backend.app.admin.crud.crud_moderation',
    'backend.app.admin.crud.crud_company_admin',
    'backend.app.career.crud.crud_question',
    'backend.app.career.crud.crud_review',
    'backend.app.career.crud.crud_company',
    'backend.app.career.crud.crud_application',
    'backend.app.career.crud.crud_prep',
    'backend.common.security.permission',
)


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch) -> FakeSupabase:
    """A fresh in-memory database, wired into every module that queries one."""
    import importlib

    fake = FakeSupabase()
    for name in SUPABASE_CONSUMERS:
        module = importlib.import_module(name)
        if hasattr(module, 'supabase'):
            monkeypatch.setattr(module, 'supabase', fake)
    return fake


@pytest.fixture(autouse=True)
def no_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the auth caches out of the tests.

    The ban and JWKS caches are the only Redis users on these paths, and the
    tests override authentication anyway.
    """
    from backend.common.security import jwt as jwt_module

    monkeypatch.setattr(jwt_module.redis_client, 'get', lambda *a, **k: None)
    monkeypatch.setattr(jwt_module.redis_client, 'set', lambda *a, **k: None)
    monkeypatch.setattr(jwt_module.redis_client, 'delete', lambda *a, **k: None)


@pytest.fixture
def app(db: FakeSupabase):
    """The real application, with the lifespan skipped.

    `register_init` opens Redis, which these tests do not need.
    """
    from backend.core.registrar import register_app

    application = register_app()
    application.router.lifespan_context = None
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app) -> TestClient:
    """Unauthenticated client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def as_user(app, client: TestClient):
    """Sign the client in as a given user, for the rest of the test."""

    def _sign_in(user_id: str, role: UserRole = UserRole.USER, email: str = 'user@example.com') -> TestClient:
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            sub=user_id, email=email, role=role, metadata={}, token=f'token-{user_id}'
        )
        return client

    return _sign_in


@pytest.fixture
def seed(db: FakeSupabase) -> dict:
    """A super admin, a plain user, a domain and an approved company."""
    admin = db.seed(USERS, {'email': 'admin@example.com', 'role': UserRole.SUPER_ADMIN.value})
    user = db.seed(USERS, {'email': 'user@example.com', 'role': UserRole.USER.value})
    domain = db.seed(DOMAINS, {'name': 'Software Engineering', 'slug': 'software-engineering'})
    company = db.seed(
        'companies',
        {'name': 'Acme', 'slug': 'acme', 'status': 'approved', 'website': 'https://acme.example'},
    )
    return {'admin': admin, 'user': user, 'domain': domain, 'company': company}


def body(response) -> dict:
    """The response envelope, as a dict."""
    return response.json()


def data(response):
    """The payload inside the envelope."""
    return response.json()['data']
