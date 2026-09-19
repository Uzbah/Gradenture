"""An in-memory stand-in for the Supabase client.

The tests exercise real flows — submit, moderate, merge, grant, revoke — so they
need a backend that remembers what was written, not a mock that returns a fixed
row. This implements the slice of PostgREST the CRUD layer actually uses:
filters, ordering, ranges, counts, insert/update/delete/upsert, the handful of
embedded selects, and the RPCs from the atomic-write migration.

The RPC implementations mirror supabase/migrations/*_atomic_rpcs.sql. Keep them
in step with that file: a change to one is a change to both.
"""

import re
import uuid
from datetime import UTC, datetime, timezone
from types import SimpleNamespace
from typing import Any

from backend.common.tables import (
    ADMIN_AUDIT_LOG,
    COMPANIES,
    COMPANY_ADMINS,
    COMPANY_EDIT_REQUESTS,
    CONTENT_FLAGS,
    FLAGGABLE,
    INTERVIEW_QUESTIONS,
    INTERVIEW_REVIEWS,
    QUESTION_UPVOTES,
    USERS,
)


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


def slugify(name: str) -> str:
    """Mirror of public.company_slug."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


# Irregular plurals, for resolving an embed's foreign key.
SINGULAR = {'companies': 'company'}

# Column defaults from the migrations. Without these, a service that relies on a
# DEFAULT clause would appear to work here and behave differently in Postgres.
COLUMN_DEFAULTS: dict[str, dict[str, Any]] = {
    'interview_questions': {'status': 'pending', 'upvotes': 0, 'is_anonymous': False},
    'interview_reviews': {'status': 'pending', 'is_anonymous': False},
    'companies': {'status': 'pending'},
    'content_flags': {'status': 'open'},
    'applications': {'status': 'applied'},
    'company_edit_requests': {'status': 'pending'},
    'prep_progress': {'completed': False},
    'users': {'role': 'user', 'onboarding_complete': False},
}


class _Result(SimpleNamespace):
    """Stands in for a PostgREST response: .data and .count."""


class _Rpc:
    """A prepared RPC call: supabase-py defers it until .execute()."""

    def __init__(self, result: _Result) -> None:
        self._result = result

    def execute(self) -> _Result:
        return self._result


class _Query:
    """One chained PostgREST query against a table in the store."""

    def __init__(self, db: 'FakeSupabase', table: str) -> None:
        self.db = db
        self.table = table
        self.filters: list[tuple[str, str, Any]] = []
        self.order_by: tuple[str, bool] | None = None
        self._range: tuple[int, int] | None = None
        self.limit_n: int | None = None
        self.want_count = False
        self.single = False
        self.embeds: list[str] = []
        self.op = 'select'
        self.payload: Any = None
        self.on_conflict: str | None = None

    # --- builders ---

    def select(self, columns: str = '*', count: str | None = None) -> '_Query':
        self.want_count = count is not None
        # Embedded resources look like `companies(*)` or `users!fkey(email)`.
        self.embeds = re.findall(r'(\w+)(?:!\w+)?\(([^)]*)\)', columns)
        return self

    def eq(self, column: str, value: Any) -> '_Query':
        self.filters.append(('eq', column, value))
        return self

    def ilike(self, column: str, pattern: str) -> '_Query':
        self.filters.append(('ilike', column, pattern))
        return self

    def order(self, column: str, desc: bool = False) -> '_Query':
        self.order_by = (column, desc)
        return self

    def limit(self, n: int) -> '_Query':
        self.limit_n = n
        return self

    def maybe_single(self) -> '_Query':
        self.single = True
        return self

    def insert(self, payload: dict | list) -> '_Query':
        self.op, self.payload = 'insert', payload
        return self

    def update(self, payload: dict) -> '_Query':
        self.op, self.payload = 'update', payload
        return self

    def upsert(self, payload: dict, on_conflict: str | None = None) -> '_Query':
        self.op, self.payload, self.on_conflict = 'upsert', payload, on_conflict
        return self

    def delete(self) -> '_Query':
        self.op = 'delete'
        return self

    def range(self, start: int, end: int) -> '_Query':
        self._range = (start, end)
        return self

    # --- execution ---

    def _matches(self, row: dict) -> bool:
        for kind, column, value in self.filters:
            actual = row.get(column)
            if kind == 'eq':
                if str(actual) != str(value):
                    return False
            elif kind == 'ilike':
                pattern = re.escape(str(value)).replace(r'\%', '.*')
                if actual is None or not re.fullmatch(pattern, str(actual), re.IGNORECASE):
                    return False
        return True

    def _rows(self) -> list[dict]:
        return self.db.store.setdefault(self.table, [])

    @staticmethod
    def _foreign_key(table: str) -> str:
        """The column an embed of `table` joins on, e.g. companies -> company_id."""
        singular = SINGULAR.get(table) or table[:-1] if table.endswith('s') else table
        return f'{singular}_id'

    def _embed(self, row: dict) -> dict:
        """Attach the embedded resources the select asked for."""
        row = dict(row)
        for name, columns in self.embeds:
            related = self.db.store.get(name, [])
            fk = self._foreign_key(name)
            key = row.get(fk) or row.get('id')
            match = next((r for r in related if str(r.get('id')) == str(key)), None)
            if match is None:
                row[name] = None
            elif columns.strip() == '*':
                row[name] = dict(match)
            else:
                wanted = [c.strip() for c in columns.split(',')]
                row[name] = {c: match.get(c) for c in wanted}
        return row

    def execute(self) -> _Result:
        rows = self._rows()

        if self.op == 'insert':
            payloads = self.payload if isinstance(self.payload, list) else [self.payload]
            created = []
            defaults = COLUMN_DEFAULTS.get(self.table, {})
            for payload in payloads:
                row = {'id': new_id(), 'created_at': now_iso(), **defaults, **payload}
                row = {k: (now_iso() if v == 'now()' else v) for k, v in row.items()}
                rows.append(row)
                created.append(dict(row))
            return _Result(data=created, count=len(created))

        if self.op == 'upsert':
            keys = [k.strip() for k in (self.on_conflict or 'id').split(',')]
            existing = next(
                (r for r in rows if all(str(r.get(k)) == str(self.payload.get(k)) for k in keys)),
                None,
            )
            if existing:
                existing.update(self.payload)
                return _Result(data=[dict(existing)], count=1)
            row = {'id': new_id(), 'created_at': now_iso(), **self.payload}
            rows.append(row)
            return _Result(data=[dict(row)], count=1)

        matched = [r for r in rows if self._matches(r)]

        if self.op == 'update':
            payload = {k: (now_iso() if v == 'now()' else v) for k, v in self.payload.items()}
            for row in matched:
                row.update(payload)
            return _Result(data=[dict(r) for r in matched], count=len(matched))

        if self.op == 'delete':
            for row in matched:
                rows.remove(row)
            return _Result(data=[dict(r) for r in matched], count=len(matched))

        # select
        if self.order_by:
            column, desc = self.order_by
            matched = sorted(matched, key=lambda r: (r.get(column) is None, r.get(column)), reverse=desc)

        total = len(matched)
        window = self._range
        if window:
            matched = matched[window[0] : window[1] + 1]
        if self.limit_n is not None:
            matched = matched[: self.limit_n]

        data = [self._embed(r) for r in matched]

        if self.single:
            return _Result(data=data[0] if data else None, count=total) if data else None

        return _Result(data=data, count=total if self.want_count else None)


class _AuthAdmin:
    """The Supabase auth admin API, as far as the backend uses it."""

    def __init__(self, db: 'FakeSupabase') -> None:
        self.db = db

    def get_user_by_id(self, user_id: str) -> SimpleNamespace:
        record = self.db.auth_users.get(user_id, {})
        return SimpleNamespace(user=SimpleNamespace(banned_until=record.get('banned_until')))

    def update_user_by_id(self, user_id: str, attrs: dict) -> None:
        record = self.db.auth_users.setdefault(user_id, {})
        if 'ban_duration' in attrs:
            duration = attrs['ban_duration']
            record['banned_until'] = None if duration == 'none' else '2099-01-01T00:00:00+00:00'
        record.update({k: v for k, v in attrs.items() if k != 'ban_duration'})

    def delete_user(self, user_id: str) -> None:
        self.db.auth_users.pop(user_id, None)

    def sign_out(self, token: str, scope: str = 'global') -> None:
        self.db.signed_out.append(token)


class _Auth:
    def __init__(self, db: 'FakeSupabase') -> None:
        self.db = db
        self.admin = _AuthAdmin(db)

    def sign_up(self, payload: dict) -> SimpleNamespace:
        email = payload['email']
        if any(r.get('email') == email for r in self.db.auth_users.values()):
            raise RuntimeError('User already registered')
        user_id = new_id()
        self.db.auth_users[user_id] = {'email': email, 'password': payload['password']}
        return SimpleNamespace(user=SimpleNamespace(id=user_id, email=email))

    def sign_in_with_password(self, payload: dict) -> SimpleNamespace:
        for user_id, record in self.db.auth_users.items():
            if record.get('email') == payload['email']:
                if record.get('password') != payload['password']:
                    raise RuntimeError('Invalid login credentials')
                return SimpleNamespace(
                    session=SimpleNamespace(access_token=f'access-{user_id}', refresh_token='refresh'),
                    user=SimpleNamespace(id=user_id, email=record['email']),
                )
        raise RuntimeError('Invalid login credentials')

    def resend(self, payload: dict) -> None:
        self.db.sent_verifications.append(payload['email'])

    def reset_password_email(self, email: str) -> None:
        self.db.sent_resets.append(email)


class FakeSupabase:
    """In-memory Supabase client: PostgREST tables, the auth API, and the RPCs."""

    def __init__(self) -> None:
        self.store: dict[str, list[dict]] = {}
        self.auth_users: dict[str, dict] = {}
        self.signed_out: list[str] = []
        self.sent_verifications: list[str] = []
        self.sent_resets: list[str] = []
        self.auth = _Auth(self)

    def table(self, name: str) -> _Query:
        return _Query(self, name)

    def seed(self, table: str, row: dict) -> dict:
        row = {'id': new_id(), 'created_at': now_iso(), **COLUMN_DEFAULTS.get(table, {}), **row}
        self.store.setdefault(table, []).append(row)
        return dict(row)

    def rows(self, table: str) -> list[dict]:
        return [dict(r) for r in self.store.get(table, [])]

    def find(self, table: str, row_id: str) -> dict | None:
        return next((dict(r) for r in self.store.get(table, []) if str(r['id']) == str(row_id)), None)

    # --- RPCs, mirroring supabase/migrations/*_atomic_rpcs.sql ---

    def rpc(self, name: str, params: dict) -> _Rpc:
        handler = getattr(self, f'_rpc_{name}', None)
        if handler is None:
            raise RuntimeError(f'unknown rpc: {name}')
        return _Rpc(_Result(data=handler(params), count=None))

    def _audit(self, actor: str, action: str, target_type: str, target_id: str | None, detail=None) -> None:
        self.seed(
            ADMIN_AUDIT_LOG,
            {
                'actor_id': actor,
                'action': action,
                'target_type': target_type,
                'target_id': target_id,
                'detail': detail,
            },
        )

    def _rpc_toggle_question_upvote(self, params: dict) -> list[dict]:
        question_id, user_id = params['p_question_id'], params['p_user_id']
        question = next((r for r in self.store.get(INTERVIEW_QUESTIONS, []) if str(r['id']) == str(question_id)), None)
        if question is None:
            return []

        upvotes = self.store.setdefault(QUESTION_UPVOTES, [])
        existing = next(
            (r for r in upvotes if str(r['question_id']) == str(question_id) and str(r['user_id']) == str(user_id)),
            None,
        )
        if existing:
            upvotes.remove(existing)
            question['upvotes'] = max(question.get('upvotes', 0) - 1, 0)
            upvoted = False
        else:
            upvotes.append({'question_id': question_id, 'user_id': user_id})
            question['upvotes'] = question.get('upvotes', 0) + 1
            upvoted = True

        return [{'upvoted': upvoted, 'upvotes': question['upvotes']}]

    def _rpc_moderate_content(self, params: dict) -> bool:
        table = FLAGGABLE[params['p_kind']]
        row = next((r for r in self.store.get(table, []) if str(r['id']) == str(params['p_content_id'])), None)
        if row is None:
            return False

        row.update(
            {
                'status': params['p_status'],
                'admin_note': params['p_admin_note'],
                'reviewed_by': params['p_actor'],
                'reviewed_at': now_iso(),
            }
        )
        self._audit(
            params['p_actor'],
            f'{params["p_kind"]}_{params["p_status"]}',
            params['p_kind'],
            params['p_content_id'],
            {'note': params['p_admin_note']},
        )
        return True

    def _rpc_resolve_content_flag(self, params: dict) -> bool:
        flag = next(
            (
                r
                for r in self.store.get(CONTENT_FLAGS, [])
                if str(r['id']) == str(params['p_flag_id']) and r.get('status') == 'open'
            ),
            None,
        )
        if flag is None:
            return False

        flag['status'] = params['p_status']
        self._audit(params['p_actor'], f'flag_{params["p_status"]}', 'flag', params['p_flag_id'])
        return True

    def _rpc_merge_company(self, params: dict) -> dict | None:
        from_id, into_id = params['p_from'], params['p_into']
        companies = self.store.setdefault(COMPANIES, [])
        loser = next((r for r in companies if str(r['id']) == str(from_id)), None)
        winner = next((r for r in companies if str(r['id']) == str(into_id)), None)
        if loser is None or winner is None:
            return None

        moved = {}
        for table in (INTERVIEW_QUESTIONS, INTERVIEW_REVIEWS):
            rows = [r for r in self.store.get(table, []) if str(r.get('company_id')) == str(from_id)]
            for row in rows:
                row['company_id'] = into_id
            moved[table] = len(rows)

        companies.remove(loser)

        detail = {
            'merged_from': from_id,
            'merged_name': loser['name'],
            'into_name': winner['name'],
            **moved,
        }
        self._audit(params['p_actor'], 'company_merged', 'company', into_id, detail)
        return detail

    def _rpc_decide_company_edit(self, params: dict) -> dict | None:
        request = next(
            (
                r
                for r in self.store.get(COMPANY_EDIT_REQUESTS, [])
                if str(r['id']) == str(params['p_request_id']) and r.get('status') == 'pending'
            ),
            None,
        )
        if request is None:
            return None

        changes = dict(request['changes'])
        if params['p_status'] == 'approved':
            name = (changes.get('name') or '').strip()
            if name:
                changes['name'] = name
                changes['slug'] = slugify(name)
            company = next(
                (r for r in self.store.get(COMPANIES, []) if str(r['id']) == str(request['company_id'])), None
            )
            if company:
                company.update({k: v for k, v in changes.items() if v is not None})

        request.update(
            {
                'status': params['p_status'],
                'admin_note': params['p_admin_note'],
                'reviewed_by': params['p_actor'],
                'reviewed_at': now_iso(),
            }
        )
        self._audit(
            params['p_actor'],
            f'company_edit_{params["p_status"]}',
            'company',
            request['company_id'],
            {'request_id': params['p_request_id'], 'changes': changes},
        )
        return {'company_id': request['company_id'], 'changes': changes}


# Tables the fake knows how to seed with sensible defaults.
SEEDABLE = (
    USERS,
    COMPANIES,
    COMPANY_ADMINS,
    COMPANY_EDIT_REQUESTS,
    INTERVIEW_QUESTIONS,
    INTERVIEW_REVIEWS,
    CONTENT_FLAGS,
    ADMIN_AUDIT_LOG,
)
