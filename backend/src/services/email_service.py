import logging
import os
import smtplib
import threading
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

PROFILE_HINT = "You can see all your submissions under Profile → My submissions."


def _deliver(to: str, subject: str, body: str) -> None:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_FROM", "noreply@gradenture.pk")
        msg["To"] = to

        with smtplib.SMTP_SSL(os.getenv("SMTP_HOST", "smtp.resend.com"),
                              int(os.getenv("SMTP_PORT", 465)), timeout=15) as server:
            server.login(os.getenv("SMTP_USER", "resend"), os.getenv("SMTP_PASS", ""))
            server.send_message(msg)
    except Exception as e:
        # never log the recipient: it may be an anonymous reviewer
        logger.error("Email send failed (%s): %s", subject, e)


def _send(to: str | None, subject: str, body: str) -> None:
    if not to:
        return
    if not os.getenv("SMTP_PASS"):
        logger.info("SMTP not configured, email skipped: %s", subject)
        return
    # ponytail: one thread per email, no retry — keeps requests fast. Move to a
    # queue if delivery must be guaranteed. Non-daemon so scripts wait for it.
    threading.Thread(target=_deliver, args=(to, subject, body)).start()


def _excerpt(text: str | None, n: int = 80) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def send_submission_confirmation(to: str | None, content_type: str, text: str) -> None:
    _send(to, f"We received your {content_type} – Gradenture",
          f"Thanks for contributing!\n\n“{_excerpt(text)}”\n\n"
          f"A moderator will review it and we'll email you the decision.\n\n{PROFILE_HINT}")


def send_moderation_decision(
    to: str | None, content_type: str, text: str, status: str, admin_note: str | None
) -> None:
    quote = f"“{_excerpt(text)}”"
    note = admin_note or "No note was added."
    if status == "approved":
        subject = f"Your {content_type} is live – Gradenture"
        body = f"Great news! Your {content_type} was approved and is now live on Gradenture.\n\n{quote}"
    elif status == "rejected":
        subject = f"Your {content_type} was not approved – Gradenture"
        body = f"Unfortunately your {content_type} was not approved.\n\n{quote}\n\nReason: {note}"
    else:  # needs_edit
        subject = f"Edit requested for your {content_type} – Gradenture"
        body = (f"A moderator asked for changes to your {content_type} before it can go live.\n\n"
                f"{quote}\n\nNote: {note}\n\nOpen Profile → My submissions to edit and resubmit it.")
    _send(to, subject, f"{body}\n\n{PROFILE_HINT}")


def send_company_edit_decision(
    to: str | None, company_name: str, status: str, admin_note: str | None
) -> None:
    if status == "approved":
        _send(to, f"Your changes to {company_name} are live – Gradenture",
              f"Your proposed profile changes for {company_name} were approved and are now live.")
    else:
        _send(to, f"Your changes to {company_name} were not approved – Gradenture",
              f"Your proposed profile changes for {company_name} were not approved.\n\n"
              f"Reason: {admin_note or 'No note was added.'}")


def send_company_approved(to: str | None, company_name: str) -> None:
    _send(to, f"{company_name} is now on Gradenture",
          f"The company you proposed, {company_name}, was approved and can now be "
          "picked when submitting questions and reviews.")


def send_deadline_reminder(to: str | None, days: int, company_name: str, role_title: str, deadline: str) -> None:
    when = "tomorrow" if days == 1 else f"in {days} days"
    _send(to, f"Deadline {when}: {company_name} – Gradenture",
          f"Heads up: your application for {role_title} at {company_name} is due {when} ({deadline}).\n\n"
          "Good luck — you've got this.")


def send_warn(to: str | None) -> None:
    _send(to, "Account warning – Gradenture",
          "Your account has received a warning for violating community guidelines.")


def send_suspend(to: str | None) -> None:
    _send(to, "Account suspended – Gradenture",
          "Your account has been suspended for violating community guidelines.")
