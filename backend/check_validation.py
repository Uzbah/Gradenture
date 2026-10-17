"""Offline checks for validation + authz guards — python check_validation.py

No server and no database needed (requests are rejected before any query).
Also collectable by pytest if it is ever installed. The smoke_*.py scripts
cover the DB-backed flows against a live dev server.
"""
import os
import time

import jwt
from fastapi.testclient import TestClient
from pydantic import ValidationError
from starlette.requests import Request

from main import app
from src.dependencies.exceptions import AppError
from src.dependencies.rate_limit import user_rate_key
from src.schemas.application_schema import ApplicationSchema, ApplicationUpdateSchema
from src.schemas.company_schema import CompanySchema
from src.schemas.question_schema import QuestionSchema
from src.services.admin_service import _require_can_discipline
from src.services.auth_service import reset_password
from src.schemas.auth_schema import ResetPasswordSchema
from src.utils.sanitize import clean_text

client = TestClient(app)
UID = "00000000-0000-4000-8000-000000000000"


def raises(exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except exc as e:
        return e
    raise AssertionError(f"{fn.__name__} did not raise {exc.__name__}")


def test_clean_text_keeps_code():
    assert clean_text("What does vector<int> v; do?") == "What does vector<int> v; do?"
    assert clean_text("a < b and c > d") == "a < b and c > d"
    assert clean_text("nul\x00byte\tok\n") == "nulbyte\tok\n"


def test_urls_must_be_http():
    assert CompanySchema(name="X", website=" https://x.example ").website == "https://x.example"
    for bad in ("javascript:alert(1)", "data:text/html,hi", "//x.example", "x.example"):
        raises(ValidationError, CompanySchema, name="X", website=bad)
    raises(ValidationError, ApplicationSchema, company_name="X", role_title="Y", job_url="javascript:x")


def test_dates():
    base = dict(domain_id=UID, company_id=UID, role_title="Dev", question_text="x" * 20,
                question_type="technical", difficulty="easy")
    assert QuestionSchema(**base, asked_date="2026-09-01")
    for bad in ("2026-13-01", "2026-09-15", "2026-9-01", "nope"):
        raises(ValidationError, QuestionSchema, **base, asked_date=bad)
    raises(ValidationError, QuestionSchema, **base, asked_date="2026-09-01", notes="n" * 501)
    raises(ValidationError, QuestionSchema, **{**base, "company_id": "nope"}, asked_date="2026-09-01")
    raises(ValidationError, ApplicationSchema, company_name="X", role_title="Y", deadline="2026-02-30")


def test_application_update_can_clear():
    assert ApplicationUpdateSchema(deadline=None).model_dump(exclude_unset=True) == {"deadline": None}
    assert ApplicationUpdateSchema(status="offer").model_dump(exclude_unset=True) == {"status": "offer"}
    raises(ValidationError, ApplicationUpdateSchema, company_name=None)
    raises(ValidationError, ApplicationUpdateSchema, status=None)


def test_malformed_ids_are_400_not_500():
    assert client.get("/api/v1/questions/not-a-uuid").status_code == 400
    assert client.get("/api/v1/reviews/1;drop").status_code == 400
    assert client.get("/api/v1/companies/abc").status_code == 400
    assert client.get("/api/v1/questions/?company_id=abc").status_code == 400
    assert client.get("/api/v1/prep/questions?domain_id=abc").status_code == 400


def test_admins_cannot_discipline_admins():
    admin, sup = {"role": "admin"}, {"role": "super_admin"}
    assert raises(AppError, _require_can_discipline, admin, {"role": "super_admin"}).status_code == 403
    assert raises(AppError, _require_can_discipline, admin, {"role": "admin"}).status_code == 403
    _require_can_discipline(admin, {"role": "user"})
    _require_can_discipline(sup, {"role": "admin"})


def test_password_change_needs_current_password():
    user = {"sub": UID, "email": "x@example.com", "amr": ["password"]}
    e = raises(AppError, reset_password, user, ResetPasswordSchema(password="new-pass-123"))
    assert e.status_code == 400 and "current_password" in e.body["errors"]
    # the recovery-link path skips that check (it then hits Supabase, so not run here)


def test_rate_key_ignores_forged_tokens():
    def req(token):
        return Request({"type": "http", "headers": [(b"authorization", f"Bearer {token}".encode())],
                        "client": ("203.0.113.9", 1)})
    claims = {"sub": UID, "aud": "authenticated", "exp": int(time.time()) + 60}
    assert user_rate_key(req(jwt.encode(claims, "wrong-secret", algorithm="HS256"))) == "203.0.113.9"
    assert user_rate_key(req("garbage")) == "203.0.113.9"
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if secret:
        assert user_rate_key(req(jwt.encode(claims, secret, algorithm="HS256"))) == UID


if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print("\n" + ("ALL PASSED" if not failed else f"{failed} FAILED"))
    raise SystemExit(1 if failed else 0)
