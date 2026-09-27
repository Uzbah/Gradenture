# frontend/src

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

- `main.tsx` — entry: `BrowserRouter` → MUI `ThemeProvider` → `AuthProvider` → `App`. No `CssBaseline`; `index.css` owns base styles.
- `App.tsx` — all routes. `Layout` = sidebar shell + guards: not logged in → `/login`; onboarding incomplete → `/onboarding`. Admin nav link is role-gated, the `/admin` route itself is not (API returns 403).
- `api.ts` — `api(path, {method, body, token})` fetch wrapper: Bearer token from `localStorage["token"]`, JSON or FormData body, flattens `{error}` / `{errors}` into `ApiError.message`, auto-logout + redirect on 401. Also the shared TS interfaces (`User`, `Question`, `Review`, `Company`, `Application`, `Flag`, `CompanyManager`, `CompanyEdit`).
- `auth.tsx` — `AuthProvider` / `useAuth()`: `user`, `loading`, `login`, `logout`, `refresh` (`GET /users/me`).
- `lookups.ts` — `useLookups()`: domains + first 50 companies, `domainName(id)` / `companyName(id)`.
- `theme.ts` — MUI theme mirroring the mono-lime CSS variables.
- `index.css` — all styling: `:root` tokens, `.shell`/`.sidebar`, `.card`, `.badge`, `.kanban`, forms.
- `vite-env.d.ts` — Vite client types.
- `components/`, `pages/` — see their CLAUDE.md.

Only `VITE_API_BASE_URL` is read from env. supabase-js is not used.
