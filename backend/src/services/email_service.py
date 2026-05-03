import logging
import smtplib
import os
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _send(to: str, subject: str, body: str) -> None:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_FROM", "noreply@careerbridge.pk")
        msg["To"] = to

        with smtplib.SMTP_SSL(os.getenv("SMTP_HOST", "smtp.resend.com"),
                               int(os.getenv("SMTP_PORT", 465))) as server:
            server.login(os.getenv("SMTP_USER", "resend"),
                         os.getenv("SMTP_PASS", ""))
            server.send_message(msg)
    except Exception as e:
        logger.error("Email send failed: %s", e)


def send_submission_confirmation(to: str) -> None:
    _send(to, "Submission received – CareerBridge",
          "Thank you! Your submission is under review and we'll notify you once it's approved.")


def send_approved(to: str, content_type: str) -> None:
    _send(to, f"Your {content_type} was approved – CareerBridge",
          f"Great news! Your {content_type} has been approved and is now live on CareerBridge.")


def send_rejected(to: str, content_type: str, admin_note: str) -> None:
    _send(to, f"Your {content_type} was not approved – CareerBridge",
          f"Unfortunately your {content_type} was not approved.\n\nReason: {admin_note}")


def send_needs_edit(to: str, content_type: str, admin_note: str) -> None:
    _send(to, f"Edit requested for your {content_type} – CareerBridge",
          f"A moderator has requested edits to your {content_type}.\n\nNote: {admin_note}\n\nPlease update and resubmit.")


def send_warn(to: str) -> None:
    _send(to, "Account warning – CareerBridge",
          "Your account has received a warning for violating community guidelines.")


def send_suspend(to: str) -> None:
    _send(to, "Account suspended – CareerBridge",
          "Your account has been suspended for violating community guidelines.")
