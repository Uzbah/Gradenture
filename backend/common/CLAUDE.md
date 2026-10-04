# backend/common — shared building blocks

Everything both feature modules (`app/admin`, `app/career`) depend on: the response
envelope, the error hierarchy, pagination, auth, enums and the base schema. Code
here must not import from `backend.app.*`, with one deliberate exception noted
below.

> Adding, renaming, deleting or repurposing a file in this folder means updating
> the tables below in the same commit.

## Top level

| File | Purpose |
|---|---|
| `enums.py` | Every closed value set the database stores as text: `ContentStatus`, `ModerationDecision`, `CompanyStatus`, `CompanyDecision`, `ContentType`, `FlagDecision`, `UserRole`, `ApplicationStatus`, `QuestionType`, `Difficulty`, `InterviewOutcome`, `SkillLevel`, `UserGoal`. |
| `schema.py` | `SchemaBase` — the pydantic base every request and response schema inherits. `use_enum_values=True`, so a validated model holds plain strings and stays JSON-serializable for PostgREST. |
| `dataclasses.py` | `CurrentUser` — the authenticated caller, with `is_admin` / `is_super_admin`. Replaces the untyped `user: dict` the old dependency returned. |
| `tables.py` | Database table-name constants, plus `FLAGGABLE`. Stands in for the model layer an ORM project would have. |
| `pagination.py` | `PageParams`, `PageData[T]`, `DependsPagination`, `paginate()` and `page_of()`. The one place page/size are validated and offsets computed. |
| `log.py` | loguru setup, the `log` object, and `InterceptHandler`, which routes stdlib logging (uvicorn, slowapi, httpx) through loguru so every line carries the trace id. |

## `response/`

| File | Purpose |
|---|---|
| `response_schema.py` | `ResponseModel`, `ResponseSchemaModel[T]`, `ResponseBase` and the `response_base` singleton. |
| `response_code.py` | `CustomResponseCode` (general), `CustomErrorCode` (application-specific, e.g. `TOKEN_EXPIRED`), `CustomResponse` (ad hoc), `StandardResponseCode` (HTTP statuses). |

Every response — success or failure — is `{code, msg, data}`. A route returns
`response_base.success(data=...)` with a `-> ResponseSchemaModel[Detail]` annotation;
list routes return `ResponseSchemaModel[PageData[Detail]]`.

## `exception/`

| File | Purpose |
|---|---|
| `errors.py` | `BaseExceptionError` and its subclasses: `RequestError` (400), `TokenError` (401), `ForbiddenError` (403), `NotFoundError` (404), `ConflictError` (409), `ServerError` (500), `GatewayError` (502), plus `CustomError` for the codes in `CustomErrorCode`. |
| `exception_handler.py` | `register_exception(app)` — handlers for the above, `RequestValidationError`, `HTTPException`, `RateLimitExceeded` and bare `Exception`, all emitting the same envelope. |

Services raise these; they never build responses or import FastAPI. Validation
errors put `{field: [message, ...]}` in `data` — the frontend renders that map
directly, so its shape is part of the API contract.

## `security/`

| File | Purpose |
|---|---|
| `jwt.py` | `decode_token()` (HS256 via the project secret, ES256 via the cached JWKS), `get_current_user()`, `is_banned()` / `invalidate_ban_cache()`, and the `CurrentUserDep` / `DependsJwtAuth` aliases. |
| `permission.py` | `require_admin`, `require_super_admin`, `require_company_manager` and their `*Dep` / `Depends*` aliases. |

`jwt.py` imports `app.admin.crud.crud_user` for the role and ban lookups — the one
allowed dependency from `common` into `app`, because the user table is where those
answers live.

Two aliases per check, by design: use `AdminDep` when the route body needs the
caller, and `dependencies=[DependsAdmin]` when it only needs the check.
