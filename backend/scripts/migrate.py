"""Apply the SQL migrations in supabase/migrations/ and record what was applied.

There is no Alembic here because there are no ORM models to autogenerate from —
the schema is hand-written SQL. What was missing was the record: nothing said
which files a given database had already seen, so "is this database up to date?"
could only be answered by reading the schema.

This script keeps that record in public.schema_migrations and applies each
pending file in its own transaction, in filename order.

Usage (from the repository root):

    python -m backend.scripts.migrate status
    python -m backend.scripts.migrate up
    python -m backend.scripts.migrate up --dry-run
    python -m backend.scripts.migrate baseline          # existing database

`supabase db push` still works; this is for knowing where a database stands.
Requires DATABASE_URL (Supabase: Project Settings -> Database -> connection string).
"""

import argparse
import hashlib
import sys
from pathlib import Path

from backend.core.conf import settings
from backend.core.path_conf import MIGRATION_DIR

TRACKING_TABLE = 'public.schema_migrations'

CREATE_TRACKING_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TRACKING_TABLE} (
  filename   text PRIMARY KEY,
  checksum   text NOT NULL,
  applied_at timestamptz NOT NULL DEFAULT now()
);
"""


def _connect():
    """Open a direct Postgres connection.

    psycopg is imported here rather than at module scope so the rest of the
    backend, which never touches Postgres directly, does not require it.
    """
    try:
        import psycopg
    except ImportError:
        sys.exit('psycopg is not installed: pip install "psycopg[binary]"')

    if not settings.DATABASE_URL:
        sys.exit('DATABASE_URL is not set (Supabase: Project Settings -> Database)')

    return psycopg.connect(settings.DATABASE_URL)


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _migration_files() -> list[Path]:
    """Every migration, in the order their names sort."""
    if not MIGRATION_DIR.is_dir():
        sys.exit(f'No migration directory at {MIGRATION_DIR}')
    return sorted(MIGRATION_DIR.glob('*.sql'))


def _applied(conn) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(CREATE_TRACKING_TABLE)
        cur.execute(f'SELECT filename, checksum FROM {TRACKING_TABLE}')
        return dict(cur.fetchall())


def _check_checksums(files: list[Path], applied: dict[str, str]) -> None:
    """Refuse to continue if an already-applied file has been edited.

    Editing an applied migration means the database and the repository disagree
    about what the schema is, and re-running the file would not fix it.
    """
    changed = [f.name for f in files if f.name in applied and applied[f.name] != _checksum(f)]
    if changed:
        sys.exit('Already-applied migrations have changed on disk: ' + ', '.join(changed))


def cmd_status() -> int:
    """Print each migration and whether this database has it."""
    files = _migration_files()
    with _connect() as conn:
        applied = _applied(conn)

    pending = 0
    for path in files:
        if path.name not in applied:
            pending += 1
            mark = 'pending'
        elif applied[path.name] != _checksum(path):
            mark = 'CHANGED'
        else:
            mark = 'applied'
        print(f'  [{mark:>7}] {path.name}')

    print(f'\n{len(files) - pending} applied, {pending} pending')
    return 0


def cmd_up(dry_run: bool = False) -> int:
    """Apply every pending migration, each in its own transaction."""
    files = _migration_files()

    with _connect() as conn:
        applied = _applied(conn)
        _check_checksums(files, applied)
        conn.commit()

        pending = [path for path in files if path.name not in applied]
        if not pending:
            print('Up to date.')
            return 0

        for path in pending:
            if dry_run:
                print(f'  would apply {path.name}')
                continue

            print(f'  applying {path.name} ...', end=' ', flush=True)
            try:
                with conn.cursor() as cur:
                    cur.execute(path.read_text())
                    cur.execute(
                        f'INSERT INTO {TRACKING_TABLE} (filename, checksum) VALUES (%s, %s)',
                        (path.name, _checksum(path)),
                    )
                conn.commit()
            except Exception as exc:
                conn.rollback()
                print('failed')
                sys.exit(f'{path.name}: {exc}')
            print('ok')

    print(f'\n{len(pending)} migration(s) {"would be " if dry_run else ""}applied.')
    return 0


def cmd_baseline() -> int:
    """Record every migration as applied without running any of them.

    For a database that already has the schema — the five original migrations
    were applied by hand before this tracking existed.
    """
    files = _migration_files()

    with _connect() as conn:
        applied = _applied(conn)
        recorded = 0
        with conn.cursor() as cur:
            for path in files:
                if path.name in applied:
                    continue
                cur.execute(
                    f'INSERT INTO {TRACKING_TABLE} (filename, checksum) VALUES (%s, %s)',
                    (path.name, _checksum(path)),
                )
                print(f'  recorded {path.name}')
                recorded += 1
        conn.commit()

    print(f'\n{recorded} migration(s) recorded as applied. Nothing was executed.')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('status', help='show which migrations this database has')

    up = sub.add_parser('up', help='apply pending migrations')
    up.add_argument('--dry-run', action='store_true', help='list what would be applied')

    sub.add_parser('baseline', help='mark all migrations applied without running them')

    args = parser.parse_args()

    if args.command == 'status':
        return cmd_status()
    if args.command == 'up':
        return cmd_up(dry_run=args.dry_run)
    return cmd_baseline()


if __name__ == '__main__':
    raise SystemExit(main())
