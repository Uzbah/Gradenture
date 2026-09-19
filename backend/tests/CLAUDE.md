# backend/tests — the test suite

Every test runs the real application over httpx's ASGI transport. No server, no
network, no Supabase project: `pytest` from the repository root is the whole
setup.

This replaces the three `smoke_*.py` scripts, which needed a running backend, a
live Supabase project with a super admin already in it, and a hardcoded path to
someone's `.env`.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the table below in the same commit.

| File | Covers |
|---|---|
| `conftest.py` | Fixtures: `db`, `app`, `client`, `as_user`, `seed`, plus the `body()` / `data()` helpers. |
| `fake_supabase.py` | The in-memory Supabase stand-in: PostgREST queries, the auth API, and the atomic-write RPCs. |
| `test_envelope.py` | The `{code, msg, data}` envelope, the error handlers, the request id header. |
| `api_v1/test_questions.py` | Browsing, filtering, paging, submission, upvotes, flags, anonymity. |
| `api_v1/test_applications.py` | The tracker, and that one user cannot reach another's rows. |
| `api_v1/test_prep.py` | Roadmaps, topic toggling, the preparedness score. |
| `api_v1/test_auth.py` | Registration, login, onboarding, and the non-committal reset replies. |
| `api_v1/test_moderation.py` | Role gating, the queue, decisions, flags, suspensions (was `smoke_admin.py`). |
| `api_v1/test_company_admin.py` | Company creation, edits, the public/admin split, merges (was `smoke_companies.py`). |
| `api_v1/test_company_manager.py` | Manager grants and queued profile edits (was `smoke_managers.py`). |

## Running

```
pytest backend/tests            # from the repository root
pytest backend/tests -k merge   # one area
```

## Fixtures

- **`db`** — a fresh `FakeSupabase`, patched into every module that holds a client
  reference. The list of those modules is `SUPABASE_CONSUMERS` in `conftest.py`;
  a new CRUD module has to be added there, or its tests will try to reach the
  network.
- **`seed`** — a super admin, a plain user, a domain and an approved company.
- **`as_user(user_id, role=..., email=...)`** — returns a client authenticated as
  that user, by overriding `get_current_user` rather than minting a token. Token
  verification itself is not under test here; the authorization rules are.
- **`client`** — the same client, unauthenticated, for checking 401s.

## The fake

`fake_supabase.py` is a small PostgREST: filters (`eq`, `ilike`), ordering,
ranges, counts, insert/update/delete/upsert, the embedded selects the CRUD layer
uses, and column defaults taken from the migrations.

Its `_rpc_*` methods mirror `supabase/migrations/*_atomic_rpcs.sql`. **A change to
one is a change to both** — otherwise the tests pass against behaviour the
database does not have.

## Conventions

- Assert on the stored row through `db.find()` / `db.rows()`, not only on the
  response. A write that returns 200 and stores nothing should fail.
- One behaviour per test, named for the behaviour rather than the endpoint.
- Where a check exists for a reason that is not obvious — 404 instead of 403 on
  another user's row, the identical reply for a known and an unknown address —
  say so in a comment.
