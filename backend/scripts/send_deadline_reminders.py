"""Email users whose tracked applications are due in 7 days or tomorrow.

    python scripts/send_deadline_reminders.py

Run once a day (Windows Task Scheduler / cron), e.g. 09:00 PKT. Only open
applications (applied / interview) are reminded. Running it twice on the same
day sends twice — schedule it once.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config.supabase import supabase  # noqa: E402
from src.services import email_service  # noqa: E402

REMIND_DAYS = (7, 1)


def main() -> None:
    today = date.today()
    sent = 0
    for days in REMIND_DAYS:
        due = (today + timedelta(days=days)).isoformat()
        apps = (
            supabase.table("applications")
            .select("user_id, company_name, role_title, deadline")
            .eq("deadline", due)
            .in_("status", ["applied", "interview"])
            .execute()
        ).data
        if not apps:
            continue

        user_ids = list({a["user_id"] for a in apps})
        emails = {
            u["id"]: u["email"]
            for u in supabase.table("users").select("id, email").in_("id", user_ids).execute().data
        }
        for a in apps:
            email_service.send_deadline_reminder(
                emails.get(a["user_id"]), days, a["company_name"], a["role_title"], a["deadline"]
            )
            sent += 1

    print(f"{sent} reminder(s) queued for {today.isoformat()}")


if __name__ == "__main__":
    main()
