# backend/app/career — the member-facing domain

Everything a logged-in user does for themselves: browsing the question bank and
interview reviews, the company registry, their private application tracker, their
prep roadmap, and the resume analyzer. Moderation of anything submitted here lives
in `app/admin`.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the tables below in the same commit.

## `api/v1/` — routes

| File | Prefix | Routes |
|---|---|---|
| `question.py` | `/questions` | list, get, submit, toggle upvote, flag |
| `review.py` | `/reviews` | list, get, submit, flag |
| `company.py` | `/companies` | list, get, list managed, submit, request profile edit |
| `application.py` | `/applications` | list, get, create, update, delete |
| `prep.py` | `/prep` | get roadmap, toggle topic |
| `resume.py` | `/resume` | analyze an upload |
| `router.py` | — | includes the six above, in that order |

## `service/` — business rules

| File | Responsibility |
|---|---|
| `question_service.py` | Question rules, plus `hide_anonymous()`, which the review service reuses. |
| `review_service.py` | Review rules. |
| `company_service.py` | Registry rules, `slugify()`, and the one-open-edit-per-company rule. |
| `application_service.py` | Tracker rules. Every method is scoped to the caller. |
| `prep_service.py` | The static `TOPICS` roadmaps and the preparedness score. |
| `resume_service.py` | Upload validation, text extraction, the Gemini prompt. |

## `crud/` — data access

| File | Table(s) |
|---|---|
| `crud_question.py` | `interview_questions`, plus the `toggle_question_upvote` RPC |
| `crud_review.py` | `interview_reviews` |
| `crud_company.py` | `companies`, `company_admins`, `company_edit_requests` |
| `crud_application.py` | `applications` |
| `crud_prep.py` | `prep_progress`, and the user's domain |

Flags are created here but worked in `app/admin`, so both go through
`app/admin/crud/crud_flag.py`.

## `schema/` — request and response models

`question.py`, `review.py`, `company.py`, `application.py`, `prep.py`, `resume.py`,
`flag.py`. Named as FBA names them: `CreateXParam` / `UpdateXParam` for input,
`GetXDetail` for output, `XSchemaBase` for the shared fields.

## Conventions

- **Anonymity is applied on the way out.** `submitted_by` is always stored;
  `hide_anonymous()` drops it from rows going to readers. Moderators still need to
  know who wrote a submission.
- **Everything submitted enters the queue as `pending`.** A service never writes
  `approved` — that is `app/admin`'s job.
- **`clean_text()` every free-text field** before it reaches the CRUD layer.
- **Ownership checks belong in the CRUD scope, not a separate read.**
  `application_dao` filters by `user_id` in the same query, and a row that is not
  the caller's is a 404 rather than a 403.
- **Timestamps stay strings** in the `Get*Detail` schemas. PostgREST already
  returns them ISO-formatted; re-parsing would risk changing what the frontend
  receives for no gain.
