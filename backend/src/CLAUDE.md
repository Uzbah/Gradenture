# backend/src — API source

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Python package imported by `../main.py` as `src`. Request flow, one direction only:

```
routers/  →  services/  →  config/supabase.py (service-role client)
   ↑              ↑
dependencies/  schemas/          utils/ (sanitize)
```

| Subfolder | Role | Rule |
|-----------|------|------|
| `routers/` | HTTP endpoints, thin | never touch the DB; call one service function |
| `services/` | business logic + Supabase queries | all authz checks and audit writes happen here |
| `schemas/` | Pydantic request models | validation only, no I/O |
| `dependencies/` | JWT auth, rate limiter, `AppError` | shared FastAPI `Depends` |
| `config/` | Supabase client singleton | the only place the service-role key is read |
| `utils/` | `clean_text()` | strip HTML from user text before insert |

`__init__.py` is empty. Conventions: responses are `{"data": ...}` or `{"message": ...}`; errors are `raise AppError(status, {"error": msg})`; every admin mutation calls `admin_service._audit()`.
