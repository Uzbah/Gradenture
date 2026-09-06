"""Company manager (per-company RBAC) smoke test — python smoke_managers.py

Needs the dev server running, migration 20260427000005 applied, and a
super_admin plus one plain user in the database.
"""
import os, time, uuid, requests, jwt
from dotenv import load_dotenv

load_dotenv()
API = f"http://localhost:{os.getenv('PORT', '3001')}/api/v1"
SUPA, SRK = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
rest = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json",
        "Prefer": "return=representation"}
fails: list[str] = []


def pick(f):
    rows = requests.get(f"{SUPA}/rest/v1/users?select=id,email&limit=1&{f}", headers=rest).json()
    if not rows:
        raise SystemExit(f"no user matching {f}")
    return rows[0]


def tok(sub):
    return jwt.encode({"sub": sub, "aud": "authenticated", "exp": int(time.time()) + 600},
                      os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")


def check(label, cond, extra=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label} {extra}")
    if not cond:
        fails.append(label)


admin, user = pick("role=eq.super_admin"), pick("role=eq.user")
A = {"Authorization": f"Bearer {tok(admin['id'])}"}
U = {"Authorization": f"Bearer {tok(user['id'])}"}
sfx = uuid.uuid4().hex[:6]

co = requests.post(f"{API}/admin/companies", headers=A,
                   json={"name": f"ZZMgr {sfx}", "industry": "Software"}).json()["data"]

# --- grant / revoke are platform-admin only --------------------------------
check("plain user cannot grant manager rights",
      requests.post(f"{API}/admin/companies/{co['id']}/managers", headers=U,
                    json={"email": user["email"]}).status_code == 403)
check("non-manager cannot edit the profile",
      requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                    json={"industry": "Sneaky"}).status_code == 403)
check("unknown email rejected",
      requests.post(f"{API}/admin/companies/{co['id']}/managers", headers=A,
                    json={"email": "nobody@nowhere.invalid"}).status_code == 404)

r = requests.post(f"{API}/admin/companies/{co['id']}/managers", headers=A,
                  json={"email": user["email"]})
check("admin grants manager rights", r.status_code == 201, r.text[:90])
check("duplicate grant rejected",
      requests.post(f"{API}/admin/companies/{co['id']}/managers", headers=A,
                    json={"email": user["email"]}).status_code == 409)
check("manager is listed",
      any(m["user_id"] == user["id"]
          for m in requests.get(f"{API}/admin/companies/{co['id']}/managers", headers=A).json()["data"]))
check("manager sees it under /companies/managed",
      any(c["id"] == co["id"]
          for c in requests.get(f"{API}/companies/managed", headers=U).json()["data"]))

# --- manager edits are queued, not applied ---------------------------------
r = requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                  json={"industry": "Fintech", "website": "https://mgr.example"})
check("manager submits an edit", r.status_code == 201, r.text[:90])
req_id = r.json().get("id")
check("edit is NOT applied yet",
      requests.get(f"{API}/companies/{co['id']}").json()["data"]["industry"] == "Software")
check("second pending edit rejected",
      requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                    json={"industry": "Again"}).status_code == 409)
check("manager cannot approve their own edit",
      requests.patch(f"{API}/admin/company-edits/{req_id}", headers=U,
                     json={"status": "approved"}).status_code == 403)
check("manager cannot set status via edit-request",
      requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                    json={"status": "approved"}).status_code in (409, 422, 400))
check("edit appears in the admin queue",
      any(e["id"] == req_id
          for e in requests.get(f"{API}/admin/company-edits", headers=A).json()["data"]))

check("admin approves the edit",
      requests.patch(f"{API}/admin/company-edits/{req_id}", headers=A,
                     json={"status": "approved"}).status_code == 200)
after = requests.get(f"{API}/companies/{co['id']}").json()["data"]
check("approved changes are now live", after["industry"] == "Fintech", after["industry"])
check("queue is empty again",
      not any(e["id"] == req_id
              for e in requests.get(f"{API}/admin/company-edits", headers=A).json()["data"]))

# --- rejection path ---------------------------------------------------------
rej = requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                    json={"industry": "Rejected Co"}).json()["id"]
requests.patch(f"{API}/admin/company-edits/{rej}", headers=A,
               json={"status": "rejected", "admin_note": "not accurate"})
check("rejected changes are not applied",
      requests.get(f"{API}/companies/{co['id']}").json()["data"]["industry"] == "Fintech")

# --- revoke -----------------------------------------------------------------
check("admin revokes manager rights",
      requests.delete(f"{API}/admin/companies/{co['id']}/managers/{user['id']}",
                      headers=A).status_code == 200)
check("revoked manager can no longer edit",
      requests.post(f"{API}/companies/{co['id']}/edit-request", headers=U,
                    json={"industry": "After revoke"}).status_code == 403)

acts = [a["action"] for a in requests.get(
    f"{SUPA}/rest/v1/admin_audit_log?select=action&order=created_at.desc&limit=10",
    headers=rest).json()]
for e in ("company_manager_granted", "company_edit_approved",
          "company_edit_rejected", "company_manager_revoked"):
    check(f"audited: {e}", e in acts)

requests.delete(f"{SUPA}/rest/v1/companies?id=eq.{co['id']}", headers=rest)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED: {fails}"))
raise SystemExit(1 if fails else 0)
