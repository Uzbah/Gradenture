# CareerBridge Frontend — CLAUDE.md

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder (or its subfolder layout), update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

React 18 + Vite + TypeScript. No UI framework, no state library — plain CSS
(`src/index.css`) and one auth context. Talks only to the FastAPI backend
(`VITE_API_BASE_URL`); supabase-js is NOT used (auth flows go through the API,
the password-recovery token is read from the URL hash in `ResetPassword.tsx`).

## Layout

```
src/
├── main.tsx            # Entry: Router + AuthProvider
├── App.tsx             # Routes + nav layout (auth/onboarding guards live here)
├── api.ts              # fetch wrapper (Bearer token, error extraction,
│                       #   auto-logout on 401) + shared TS types
├── auth.tsx            # AuthProvider / useAuth (user, login, logout, refresh)
├── lookups.ts          # useLookups(): domains + companies id→name maps
├── index.css           # All styling (CSS variables, .card/.badge/.kanban etc.)
└── pages/              # One file per route, forms inlined in the page
```

Conventions: token in localStorage; month fields use `<input type="month">`
and send `YYYY-MM-01`; API errors are shown via `err.message` (already
flattened by `api.ts`); optimistic updates then reconcile from the response.

Run: `npm install`, `npm run dev` (5173). Build: `npm run build`
(`tsc -b && vite build`) — output `dist/` is served by the backend in prod
(`.env.production` sets `VITE_API_BASE_URL=/api/v1`).

## ⚠️ SETUP REQUIRED

The original Supabase project was deleted. After the backend team creates a
new one (see `backend/CLAUDE.md`), update `.env`:

- `VITE_SUPABASE_URL` — new project URL
- `VITE_SUPABASE_ANON_KEY` — new anon key
- `VITE_API_BASE_URL=http://localhost:3001/api/v1` (dev; already set)

Note: the two `VITE_SUPABASE_*` vars are currently unused by the code (kept
for when supabase-js is introduced, e.g. Google OAuth or Realtime). Only
`VITE_API_BASE_URL` matters today.

## Implemented pages

Login (+ resend verification), Register, ForgotPassword, ResetPassword,
Onboarding, Dashboard (stats + latest questions + prep score), Questions
(filters/submit/upvote/flag + inline add-company; question-pool section
under the same filters), Reviews, Applications
(5-column kanban), Prep (progress ring + topic checklist + question-bank
practice list for the user's domain), Resume (AI
analyzer), Companies (registry list + company profile with community + question-bank questions/reviews
and a manager-only "propose changes" form), Admin (moderation queue incl.
pending companies and profile edits, flags, companies, user management,
role-gated).

## Remaining / known gaps

- **Company select is capped at 50** (`lookups.ts`, `ponytail:` comment) —
  the submission forms still use a plain <select>; `/companies` has server-side
  search (`?q=`) that these could reuse via MUI Autocomplete.
- **No profile page** (PRD 5.1.3) — can't edit name/avatar/university after
  onboarding; no contribution stats.
- **No "my submissions" view** — users can't see their pending/rejected/
  needs_edit questions or resubmit after an edit request (backend endpoint
  also missing).
- **Admin gaps mirror the backend**: no analytics dashboard, no suspend-
  duration choice. (Flags tab, pending-companies approval and unsuspend exist.)
- **Kanban is dropdown-move, not drag-and-drop** — deliberate; add dnd only
  if users ask.
- **Flag/moderation notes use `window.prompt`** — fine for MVP, replace with
  a modal if design matters.
- **No keyword search box** on Questions (backend doesn't support it yet).
- **No token refresh** — the Supabase access token expires (~1h) and the app
  logs you out; wire refresh_token rotation if sessions feel too short.
- **Phase 2**: preparedness radar chart, activity streak, AI mock interview
  UI, mentorship, leaderboard.
- **No tests.**
