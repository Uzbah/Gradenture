"""Session refresh + My submissions / resubmit smoke test — python smoke_profile.py

Needs the dev server running and a super_admin in the database. Creates a
throwaway confirmed user (smoke-<id>@example.com), logs in for real, and deletes
the user and its content at the end. Emails go only to that example.com address.
"""
import os
import time
import uuid

import jwt
import requests
from dotenv import load_dotenv

load_dotenv()
API = f"http://localhost:{os.getenv('PORT', '3001')}/api/v1"
SUPA, SRK = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
rest = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json",
        "Prefer": "return=representation"}
fails: list[str] = []


def check(label, cond, extra=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label} {extra}")
    if not cond:
        fails.append(label)


def one(path):
    rows = requests.get(f"{SUPA}/rest/v1/{path}", headers=rest).json()
    if not rows:
        raise SystemExit(f"nothing at {path}")
    return rows[0]


admin = one("users?select=id&role=eq.super_admin&limit=1")
A = {"Authorization": "Bearer " + jwt.encode(
    {"sub": admin["id"], "aud": "authenticated", "exp": int(time.time()) + 600},
    os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")}
domain = one("domains?select=id&limit=1")["id"]
company = one("companies?select=id&status=eq.approved&limit=1")["id"]

# --- throwaway user, registered the way the app does it --------------------
email, password = f"smoke-{uuid.uuid4().hex[:8]}@example.com", "Smoke-pass-123"
uid = requests.post(f"{SUPA}/auth/v1/admin/users", headers=rest,
                    json={"email": email, "password": password, "email_confirm": True}).json()["id"]
requests.post(f"{SUPA}/rest/v1/users", headers=rest,
              json={"id": uid, "email": email, "role": "user", "onboarding_complete": True})

try:
    # --- login + refresh ---------------------------------------------------
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password})
    check("real login works", r.status_code == 200, r.text[:100])
    session = r.json()
    check("login returns a refresh token", bool(session.get("refresh_token")))
    check("admin endpoints still work after a user logged in (shared-client bug)",
          requests.get(f"{API}/admin/queue", headers=A).status_code == 200)

    r = requests.post(f"{API}/auth/refresh", json={"refresh_token": session["refresh_token"]})
    check("refresh returns a new session", r.status_code == 200, r.text[:100])
    new = r.json()
    check("refresh token rotated", new.get("refresh_token") not in (None, session["refresh_token"]))
    U = {"Authorization": f"Bearer {new['access_token']}"}
    check("new access token is accepted", requests.get(f"{API}/users/me", headers=U).status_code == 200)
    check("garbage refresh token -> 401",
          requests.post(f"{API}/auth/refresh", json={"refresh_token": "nope"}).status_code == 401)

    # --- submit -> needs_edit -> my submissions -> resubmit ----------------
    q = requests.post(f"{API}/questions/", headers=U, json={
        "domain_id": domain, "company_id": company, "role_title": "Smoke Tester",
        "question_text": "Explain how a smoke test differs from a regression test",
        "question_type": "technical", "difficulty": "easy", "asked_date": "2026-09-01"}).json()["id"]
    mine = requests.get(f"{API}/users/me/submissions", headers=U).json()["data"]
    check("pending question shows in My submissions",
          any(x["id"] == q and x["status"] == "pending" for x in mine["questions"]))
    check("resubmit refused while pending",
          requests.patch(f"{API}/questions/{q}", headers=U,
                         json={"question_text": "x" * 25}).status_code == 409)

    requests.patch(f"{API}/admin/questions/{q}", headers=A,
                   json={"status": "needs_edit", "admin_note": "Add the company context"})
    mine = requests.get(f"{API}/users/me/submissions", headers=U).json()["data"]
    row = next(x for x in mine["questions"] if x["id"] == q)
    check("needs_edit + moderator note visible to submitter",
          row["status"] == "needs_edit" and row["admin_note"] == "Add the company context")

    check("another user cannot resubmit it (404)",
          requests.patch(f"{API}/questions/{q}", headers=A,
                         json={"question_text": "y" * 25}).status_code == 404)
    r = requests.patch(f"{API}/questions/{q}", headers=U,
                       json={"question_text": "Explain how a smoke test differs from a regression test at a startup"})
    check("owner resubmits", r.status_code == 200, r.text[:100])
    row = one(f"interview_questions?id=eq.{q}&select=status,question_text")
    check("back to pending with new text", row["status"] == "pending" and "startup" in row["question_text"])
    check("double resubmit refused",
          requests.patch(f"{API}/questions/{q}", headers=U,
                         json={"question_text": "z" * 25}).status_code == 409)
finally:
    requests.delete(f"{SUPA}/rest/v1/interview_questions?submitted_by=eq.{uid}", headers=rest)
    requests.delete(f"{SUPA}/rest/v1/users?id=eq.{uid}", headers=rest)
    requests.delete(f"{SUPA}/auth/v1/admin/users/{uid}", headers=rest)

print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED: {fails}"))
raise SystemExit(1 if fails else 0)
