import os, time, uuid, requests, jwt
from dotenv import load_dotenv
load_dotenv(r"c:\Users\DELL\Desktop\Gradenture\neo-staging\Gradenture\backend\.env")
API = "http://localhost:3001/api/v1"
SUPA, SRK = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
rest = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json",
        "Prefer": "return=representation"}
def pick(f):
    return requests.get(f"{SUPA}/rest/v1/users?select=id&limit=1&{f}", headers=rest).json()[0]["id"]
ADMIN = pick("role=eq.super_admin"); USER = pick("role=eq.user")
tok = lambda s: jwt.encode({"sub": s, "aud": "authenticated", "exp": int(time.time())+600},
                           os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")
A = {"Authorization": f"Bearer {tok(ADMIN)}"}; U = {"Authorization": f"Bearer {tok(USER)}"}
fails = []
def check(label, cond, extra=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label} {extra}"); fails.append(label) if not cond else None

sfx = uuid.uuid4().hex[:6]
# create (auto-approved, admin only)
r = requests.post(f"{API}/admin/companies", headers=A,
                  json={"name": f"ZZKeep {sfx}", "industry": "Software", "website": "https://a.example"})
check("admin creates company", r.status_code == 201, r.text[:100])
keep = r.json()["data"]
check("admin-created skips the queue", keep["status"] == "approved", keep["status"])
check("plain user cannot create",
      requests.post(f"{API}/admin/companies", headers=U, json={"name": f"ZZNope {sfx}"}).status_code == 403)
check("duplicate name rejected",
      requests.post(f"{API}/admin/companies", headers=A, json={"name": f"zzkeep {sfx}"}).status_code == 409)

# edit
r = requests.patch(f"{API}/admin/companies/{keep['id']}", headers=A,
                   json={"industry": "Fintech", "logo_url": "https://a.example/logo.png"})
check("admin edits profile fields", r.status_code == 200 and r.json()["data"]["industry"] == "Fintech",
      r.json().get("data", {}).get("industry", r.text[:80]))
check("untouched fields survive", r.json()["data"]["website"] == "https://a.example")

# rename regenerates slug
r = requests.patch(f"{API}/admin/companies/{keep['id']}", headers=A, json={"name": f"ZZKeep Renamed {sfx}"})
check("rename regenerates slug", r.json()["data"]["slug"] == f"zzkeep-renamed-{sfx}", r.json()["data"]["slug"])

# admin list shows pending too
dupe = requests.post(f"{SUPA}/rest/v1/companies", headers=rest, json={
    "name": f"ZZDupe {sfx}", "slug": f"zzdupe-{sfx}", "status": "pending"}).json()[0]
adm = requests.get(f"{API}/admin/companies", headers=A, params={"q": "zz", "limit": 50}).json()
pub = requests.get(f"{API}/companies/", params={"q": "zz", "limit": 50}).json()
check("admin list includes pending", any(c["id"] == dupe["id"] for c in adm["data"]))
check("public list still hides pending", not any(c["id"] == dupe["id"] for c in pub["data"]))

# seed content on the dupe, then merge it away
dom = requests.get(f"{SUPA}/rest/v1/domains?select=id&limit=1", headers=rest).json()[0]["id"]
q = requests.post(f"{SUPA}/rest/v1/interview_questions", headers=rest, json={
    "submitted_by": USER, "domain_id": dom, "company_id": dupe["id"], "role_title": "SWE",
    "question_text": "Explain the CAP theorem in your own words please",
    "question_type": "technical", "difficulty": "medium", "asked_date": "2026-01-01",
    "status": "approved"}).json()[0]
check("merge into self rejected",
      requests.post(f"{API}/admin/companies/{dupe['id']}/merge", headers=A,
                    json={"into_id": dupe["id"]}).status_code == 400)
r = requests.post(f"{API}/admin/companies/{dupe['id']}/merge", headers=A, json={"into_id": keep["id"]})
check("merge succeeds", r.status_code == 200, r.text[:100])
check("merge moved the question", r.json()["data"]["interview_questions"] == 1, str(r.json().get("data")))
moved = requests.get(f"{SUPA}/rest/v1/interview_questions?id=eq.{q['id']}&select=company_id",
                     headers=rest).json()[0]
check("question now points at survivor", moved["company_id"] == keep["id"])
check("duplicate deleted",
      requests.get(f"{SUPA}/rest/v1/companies?id=eq.{dupe['id']}&select=id", headers=rest).json() == [])

acts = [a["action"] for a in requests.get(
    f"{SUPA}/rest/v1/admin_audit_log?select=action&order=created_at.desc&limit=8", headers=rest).json()]
for e in ("company_created", "company_updated", "company_merged"):
    check(f"audited: {e}", e in acts)

requests.delete(f"{SUPA}/rest/v1/interview_questions?id=eq.{q['id']}", headers=rest)
requests.delete(f"{SUPA}/rest/v1/companies?id=eq.{keep['id']}", headers=rest)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED: {fails}"))
