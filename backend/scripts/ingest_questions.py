"""Import curated interview questions from a CSV into public.question_bank.

    python scripts/ingest_questions.py scripts/data/interview_pool_2026-09.csv
    python scripts/ingest_questions.py scripts/data/interview_pool_2026-09.csv --commit --actor admin@example.com

Dry run by default (reads the DB, writes nothing). --commit creates missing
companies as approved (the admin running the import is the approval), upserts
the questions and writes audit rows. Re-running is safe: duplicates are skipped.
Undo a batch with: DELETE FROM question_bank WHERE source = '<csv file stem>';

Uses the service-role client and never signs in, so it is unaffected by
supabase-py swapping the client's auth header on login.
"""
import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ValidationError, field_validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config.supabase import maybe_row, supabase  # noqa: E402
from src.services.admin_service import _audit  # noqa: E402
from src.services.companies_service import _slug  # noqa: E402
from src.utils.sanitize import clean_text  # noqa: E402

BATCH = 500


class Row(BaseModel):
    domain_slug:   str
    role_title:    str
    company:       Optional[str] = None
    question_text: str
    question_type: Literal["technical", "behavioural", "hr", "case_study"]
    difficulty:    Optional[Literal["easy", "medium", "hard"]] = None

    @field_validator("company", "difficulty", mode="before")
    @classmethod
    def blank_to_none(cls, v: object) -> object:
        return (v.strip() or None) if isinstance(v, str) else v

    @field_validator("question_text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = " ".join(clean_text(v).split())
        if len(v) < 20:
            raise ValueError("must be at least 20 characters")
        return v

    @field_validator("role_title")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip()
        if not 1 <= len(v) <= 100:
            raise ValueError("must be 1-100 characters")
        return v


def content_hash(text: str) -> str:
    return hashlib.sha256(re.sub(r"[^a-z0-9]+", " ", text.lower()).strip().encode()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", type=Path)
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--actor", help="email of the admin running the import (required with --commit)")
    args = ap.parse_args()
    source = args.csv_path.stem

    actor_id = None
    if args.commit:
        actor = args.actor and maybe_row(
            supabase.table("users").select("id, role").eq("email", args.actor.strip().lower())
        )
        if not actor or actor["role"] not in ("admin", "super_admin"):
            sys.exit("--commit needs --actor <email of an admin or super_admin>")
        actor_id = actor["id"]

    domains = {d["slug"]: d["id"] for d in supabase.table("domains").select("id, slug").execute().data}

    rows: list[tuple[Row, str]] = []
    rejects: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    with args.csv_path.open(newline="", encoding="utf-8-sig") as f:
        for line, raw in enumerate(csv.DictReader(f), start=2):
            try:
                r = Row(**raw)
            except ValidationError as e:
                rejects.append(f"line {line}: {e.errors()[0]['loc'][0]} {e.errors()[0]['msg']}")
                continue
            if r.domain_slug not in domains:
                rejects.append(f"line {line}: unknown domain '{r.domain_slug}'")
                continue
            h = content_hash(r.question_text)
            key = (r.domain_slug, _slug(r.company or ""), h)
            if key in seen:
                rejects.append(f"line {line}: duplicate within file")
                continue
            seen.add(key)
            rows.append((r, h))

    # Exact slug match, not ilike: names like "1PercentLabs" must not wildcard-match.
    companies: dict[str, str] = {}
    to_create: list[str] = []
    for name in sorted({r.company for r, _ in rows if r.company}):
        hit = maybe_row(supabase.table("companies").select("id, status").eq("slug", _slug(name)))
        if hit:
            companies[name] = hit["id"]
            if hit["status"] != "approved":
                print(f"warning: '{name}' exists but is {hit['status']} — questions will link to it anyway")
        else:
            to_create.append(name)

    print(f"source:            {source}")
    print(f"valid rows:        {len(rows)}")
    print(f"rejected:          {len(rejects)}")
    for msg in rejects:
        print(f"  - {msg}")
    print(f"companies found:   {len(companies)}")
    print(f"companies to add:  {len(to_create)} {to_create}")

    if not args.commit:
        print("\nDry run — nothing written. Re-run with --commit --actor <admin email>.")
        return

    for name in to_create:
        company = supabase.table("companies").insert(
            {"name": name, "slug": _slug(name), "status": "approved"}
        ).execute().data[0]
        companies[name] = company["id"]
        _audit(actor_id, "company_created", "company", company["id"], {"name": name, "source": source})

    payload = [{
        "domain_id":     domains[r.domain_slug],
        "company_id":    companies[r.company] if r.company else None,
        "role_title":    r.role_title,
        "question_text": r.question_text,
        "question_type": r.question_type,
        "difficulty":    r.difficulty,
        "source":        source,
        "content_hash":  h,
    } for r, h in rows]

    inserted = 0
    for i in range(0, len(payload), BATCH):
        res = supabase.table("question_bank").upsert(
            payload[i:i + BATCH],
            on_conflict="domain_id,company_id,content_hash",
            ignore_duplicates=True,
        ).execute()
        inserted += len(res.data or [])

    counts = {"inserted": inserted, "skipped_existing": len(payload) - inserted,
              "rejected": len(rejects), "companies_created": len(to_create)}
    _audit(actor_id, "question_bank_imported", "question_bank", None, {"source": source, **counts})
    print(f"\nCommitted: {counts}")


if __name__ == "__main__":
    main()
