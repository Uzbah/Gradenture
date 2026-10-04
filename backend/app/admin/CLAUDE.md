# backend/app/admin — accounts and moderation

Authentication, the caller's own profile, and everything a platform admin does:
the moderation queue, content flags, the company registry's administrative side,
and user role and suspension management.

Named `admin` after fastapi-best-architecture's own module, which likewise holds
auth alongside the system-administration routes. Not every route here requires an
admin: `/auth/*`, `/users/me`, `/users/onboarding` and `/domains` are for any
signed-in user.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the tables below in the same commit.

## `api/v1/` — routes

| File | Prefix | Routes |
|---|---|---|
| `auth/auth.py` | `/auth` | register, login, logout, reset-password, forgot-password, resend-verification |
| `sys/user.py` | — | `/users/me`, `/users/onboarding`, `/domains` |
| `sys/moderation.py` | `/admin` | queue, decide a question, decide a review |
| `sys/flag.py` | `/admin` | list open flags, close a flag |
| `sys/company_admin.py` | `/admin` | company list/create/update/merge, managers, profile edit requests |
| `sys/user_admin.py` | `/admin` | user list, role, warn, suspend, unsuspend |
| `api/router.py` | — | includes `auth/` then `sys/` |

## `service/` — business rules

| File | Responsibility |
|---|---|
| `auth_service.py` | Registration and sessions over Supabase Auth, including the compensating rollback when the profile write fails. |
| `user_service.py` | The caller's own profile, onboarding, the domain list. |
| `moderation_service.py` | Decisions on submitted questions and reviews. |
| `flag_service.py` | Reported content: listing and closing. |
| `company_admin_service.py` | Company approval, edits, merges, managers, edit requests. |
| `user_admin_service.py` | Roles, warnings, suspensions. |

Six services in place of the single 395-line `admin_service.py`, split along the
lines the routes already grouped by.

## `crud/` — data access

| File | Table(s) |
|---|---|
| `crud_user.py` | `users`, `domains`, and the Supabase auth admin API |
| `crud_moderation.py` | the pending queue, plus the `moderate_content` RPC |
| `crud_flag.py` | `content_flags`, plus the `resolve_content_flag` RPC |
| `crud_company_admin.py` | `companies`, `company_admins`, `company_edit_requests`, plus the `merge_company` and `decide_company_edit` RPCs |
| `crud_audit.py` | `admin_audit_log` |

## `schema/`

`auth.py`, `user.py`, `moderation.py`, `company_admin.py`.

## Conventions

- **Every admin mutation is audited.** Actions taken through an RPC write their
  audit row inside the same transaction; the rest call `audit_dao.record()`.
  An audit write is never wrapped in try/except — an unrecorded decision is worse
  than a failed one.
- **Supabase auth is authoritative for credentials and login blocking;
  `public.users` is authoritative for the role.** `user_metadata.role` is a mirror
  for clients that read the token, and `users.suspended_at` is a display mirror so
  the admin list needs no auth API call per row. Both mirrors may lag, and failures
  writing them are logged rather than raised.
- **A suspension change invalidates the ban cache** (`invalidate_ban_cache`), or it
  would take up to `CACHE_BAN_TTL` to take effect.
- **Self-protection rules live in the service**: a super admin cannot demote
  themselves, and nobody can suspend themselves.
- **`forgot-password` and `resend-verification` answer identically** whether or not
  the address is registered — the reply must not reveal who has an account.
