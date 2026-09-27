# backend/src/config

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

- `supabase.py` — builds the module-level `supabase: Client` from `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (loads `backend/.env` by absolute path first). Raises at import if either is missing. Also exports `maybe_row(query)`: runs `.maybe_single().execute()` and returns the row dict or `None` (supabase-py 2.x returns `None` instead of a response when nothing matches).
- `__init__.py` — empty.

Security note: this client is **service-role**, so it bypasses RLS. Never hand it, or anything derived from it, to code paths that should be user-scoped without an explicit ownership/role check in the calling service.
