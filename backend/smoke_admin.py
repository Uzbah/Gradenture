"""Admin portal smoke test — run against a live dev backend: python smoke_admin.py

Needs the server running on PORT and a super_admin plus one plain user in the
database. Creates a throwaway company and flag, then deletes them; the
admin_audit_log rows it produces are left in place on purpose.
"""
import os
import time
import uuid

import jwt
import requests
from dotenv import load_dotenv

load_dotenv()
API = f"http://localhost:{os.getenv('PORT', '3001')}/api/v1"
SECRET = os.environ["SUPABASE_JWT_SECRET"]
SUPA, SRK = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
rest = {"apikey": SRK, "Authorization": f"Bearer {SRK}"}
fails: list[str] = []


def pick(role_filter: str) -> str:
    rows = requests.get(
        f"{SUPA}/rest/v1/users?select=id&limit=1&{role_filter}", headers=rest
    ).json()
    if not rows:
        raise SystemExit(f"no user matching {role_filter}")
    return rows[0]["id"]


def token(sub: str) -> str:
    return jwt.encode(
        {"sub": sub, "aud": "authenticated", "exp": int(time.time()) + 600},
        SECRET,
        algorithm="HS256",
    )


def check(label: str, cond: bool, extra: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {label} {extra}")
    if not cond:
        fails.append(label)


ADMIN_ID = pick("role=eq.super_admin")
USER_ID = pick("role=eq.user")
A = {"Authorization": f"Bearer {token(ADMIN_ID)}"}
U = {"Authorization": f"Bearer {token(USER_ID)}"}

# role gating
check("plain user refused by /admin/queue",
      requests.get(f"{API}/admin/queue", headers=U).status_code == 403)
check("admin allowed into /admin/queue",
      requests.get(f"{API}/admin/queue", headers=A).status_code == 200)

# company: propose -> queue -> approve
r = requests.post(f"{API}/companies/", headers=U,
                  json={"name": f"ZZ Smoke Test Co {uuid.uuid4().hex[:6]}"})
check("user can propose a company", r.status_code == 201, r.text[:120])
cid = r.json().get("id")
queue = requests.get(f"{API}/admin/queue", headers=A).json()["data"]
check("queue exposes pending companies",
      any(c["id"] == cid for c in queue.get("companies", [])))
check("admin approves the company",
      requests.patch(f"{API}/admin/companies/{cid}", headers=A).status_code == 200)
check("company now publicly listed",
      requests.get(f"{SUPA}/rest/v1/companies?id=eq.{cid}&select=status",
                   headers=rest).json()[0]["status"] == "approved")

# flags: raise -> list -> dismiss
flag = requests.post(
    f"{SUPA}/rest/v1/content_flags",
    headers={**rest, "Content-Type": "application/json", "Prefer": "return=representation"},
    json={"reported_by": USER_ID, "content_type": "question",
          "content_id": str(uuid.uuid4()), "reason": "smoke test flag"},
).json()[0]
row = next((f for f in requests.get(f"{API}/admin/flags", headers=A).json()["data"]
            if f["id"] == flag["id"]), None)
check("open flag appears in /admin/flags", row is not None)
check("deleted content degrades gracefully", row is not None and row.get("content") is None)
check("flag can be dismissed",
      requests.patch(f"{API}/admin/flags/{flag['id']}", headers=A,
                     json={"status": "dismissed"}).status_code == 200)
check("re-dismissing a closed flag 404s",
      requests.patch(f"{API}/admin/flags/{flag['id']}", headers=A,
                     json={"status": "dismissed"}).status_code == 404)

# self-action guards + suspension round-trip
check("super admin cannot demote themselves",
      requests.patch(f"{API}/admin/users/{ADMIN_ID}/role", headers=A,
                     json={"role": "user"}).status_code == 400)
check("admin cannot suspend themselves",
      requests.patch(f"{API}/admin/users/{ADMIN_ID}/suspend", headers=A).status_code == 400)
check("suspend/unsuspend round-trips",
      requests.patch(f"{API}/admin/users/{USER_ID}/suspend", headers=A).status_code == 200
      and requests.patch(f"{API}/admin/users/{USER_ID}/unsuspend", headers=A).status_code == 200)
check("suspended_at cleared after unsuspend",
      requests.get(f"{SUPA}/rest/v1/users?id=eq.{USER_ID}&select=suspended_at",
                   headers=rest).json()[0]["suspended_at"] is None)

# every admin mutation is audited
actions = [a["action"] for a in requests.get(
    f"{SUPA}/rest/v1/admin_audit_log?select=action&order=created_at.desc&limit=10",
    headers=rest).json()]
for expected in ("company_approved", "flag_dismissed", "user_suspended", "user_unsuspended"):
    check(f"audit row written: {expected}", expected in actions)

requests.delete(f"{SUPA}/rest/v1/companies?id=eq.{cid}", headers=rest)
requests.delete(f"{SUPA}/rest/v1/content_flags?id=eq.{flag['id']}", headers=rest)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED: {fails}"))
raise SystemExit(1 if fails else 0)
