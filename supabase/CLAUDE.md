# supabase

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Supabase is hosted (not a container). This folder holds only `migrations/` — the single source of truth for schema, constraints, and RLS. There is no `seed.sql` and no `config.toml` yet.

Apply with `supabase db push` against the linked project, or paste each file into the SQL editor **in filename order**. After applying, bootstrap the first super admin by hand:

```sql
UPDATE public.users SET role = 'super_admin' WHERE email = 'you@example.com';
```

Rules: one migration per schema change; never edit an applied migration — add a new one. Any new table must enable RLS. Keep `CHECK` constraints in sync with the `Literal[...]` types in `backend/src/schemas`.
