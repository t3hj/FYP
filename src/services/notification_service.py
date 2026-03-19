"""
Notification Service
====================
Sends email notifications to residents when the council updates the status
of their report. Entirely optional — if SMTP credentials are not configured
in .streamlit/secrets.toml the service silently does nothing.

Required secrets (all optional — omit to disable notifications):
    SMTP_HOST       = "smtp.gmail.com"
    SMTP_PORT       = "587"
    SMTP_USER       = "your-address@gmail.com"
    SMTP_PASSWORD   = "your-app-password"
    SMTP_FROM_NAME  = "Local Lens"      # display name shown to recipient

For Gmail, SMTP_PASSWORD must be an App Password, not your account password.
Generate one at: https://myaccount.google.com/apppasswords
"""

from __future__ import annotations

import logging
import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from config.settings import SUPABASE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)

# ── Read SMTP config from Streamlit secrets ───────────────────────────────────
try:
    import streamlit as st
    _SMTP_HOST      = st.secrets.get("SMTP_HOST",      "smtp.gmail.com")
    _SMTP_PORT      = int(st.secrets.get("SMTP_PORT",  587))
    _SMTP_USER      = st.secrets.get("SMTP_USER",      "")
    _SMTP_PASSWORD  = st.secrets.get("SMTP_PASSWORD",  "")
    _FROM_NAME      = st.secrets.get("SMTP_FROM_NAME", "Local Lens")
except Exception:
    _SMTP_HOST     = "smtp.gmail.com"
    _SMTP_PORT     = 587
    _SMTP_USER     = ""
    _SMTP_PASSWORD = ""
    _FROM_NAME     = "Local Lens"

_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE,
)

# Human-readable labels and colours for each status
_STATUS_META = {
    "Open":        ("🔴 Open",        "#ef4444", "has been reopened"),
    "In Progress": ("🟡 In Progress", "#f97316", "is now being investigated"),
    "Resolved":    ("🟢 Resolved",    "#22c55e", "has been resolved"),
    "Won't Fix":   ("⚫ Won't Fix",   "#6b7280", "has been marked as Won't Fix"),
}


# ── Public API ────────────────────────────────────────────────────────────────

def notify_status_change(
    report: dict,
    new_status: str,
    council_notes: str = "",
) -> bool:
    """
    Send a status-change notification for a report.

    Parameters
    ----------
    report       : the full report dict (needs reporter_id, title, location, id)
    new_status   : the new status string
    council_notes: optional council note to include in the email body

    Returns True if an email was sent, False otherwise.
    """
    if not _smtp_configured():
        return False

    reporter_id = report.get("reporter_id")
    recipient   = _resolve_email(reporter_id)
    if not recipient:
        return False

    subject, html_body = _build_email(report, new_status, council_notes)

    return _send(recipient, subject, html_body)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _smtp_configured() -> bool:
    return bool(_SMTP_USER and _SMTP_PASSWORD)


def _resolve_email(reporter_id: str | None) -> str | None:
    """
    Return an email address for the reporter, or None if we can't find one.

    - If reporter_id looks like an email, use it directly.
    - If it looks like a UUID, call the Supabase admin API to look up the user.
    - Otherwise return None.
    """
    if not reporter_id:
        return None

    rid = str(reporter_id).strip()

    # Direct email
    if "@" in rid:
        return rid

    # UUID → Supabase admin user lookup
    if _UUID_RE.match(rid):
        return _lookup_email_by_uuid(rid)

    return None


def _lookup_email_by_uuid(uuid: str) -> str | None:
    """Call Supabase admin API to get the email for a user UUID."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{uuid}"
        resp = requests.get(
            url,
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            timeout=8,
        )
        if resp.status_code == 200:
            return resp.json().get("email")
        if resp.status_code in (401, 403):
            logger.warning(
                "Local Lens notifications: Supabase returned %s when looking up "
                "user email. Make sure SUPABASE_KEY is a service_role key, not "
                "an anon key, to enable resident notifications.",
                resp.status_code,
            )
    except Exception as exc:
        logger.debug("Email lookup failed for UUID %s: %s", uuid, exc)
    return None


def _build_email(
    report: dict,
    new_status: str,
    council_notes: str,
) -> tuple[str, str]:
    """Return (subject, html_body) for the notification email."""
    title    = str(report.get("title") or "Your report").strip()
    location = str(report.get("location") or "").strip()
    report_id = report.get("id", "")

    status_label, status_colour, status_verb = _STATUS_META.get(
        new_status,
        (new_status, "#6b7280", "has been updated"),
    )

    notes_block = ""
    if council_notes and council_notes.strip():
        notes_block = f"""
        <tr>
          <td style="padding:16px 24px 0;">
            <div style="border-radius:8px;background:#f1f5f9;padding:14px 16px;">
              <div style="font-size:12px;font-weight:600;color:#64748b;
                          text-transform:uppercase;letter-spacing:0.06em;
                          margin-bottom:6px;">Council Note</div>
              <div style="font-size:14px;color:#334155;line-height:1.6;">
                {council_notes.strip()}
              </div>
            </div>
          </td>
        </tr>"""

    subject = f"Local Lens — your report {status_verb}: {title}"

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:system-ui,-apple-system,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:16px;
                      box-shadow:0 4px 24px rgba(0,0,0,0.08);
                      overflow:hidden;max-width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#4f46e5,#a855f7);
                       padding:28px 24px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:#ffffff;
                          letter-spacing:-0.02em;">📸 Local Lens</div>
              <div style="font-size:13px;color:rgba(255,255,255,0.8);margin-top:4px;">
                Community Issue Reporting
              </div>
            </td>
          </tr>

          <!-- Status badge -->
          <tr>
            <td style="padding:28px 24px 0;text-align:center;">
              <span style="display:inline-block;background:{status_colour}18;
                           color:{status_colour};border:1px solid {status_colour}44;
                           border-radius:999px;padding:6px 18px;
                           font-size:14px;font-weight:700;">
                {status_label}
              </span>
            </td>
          </tr>

          <!-- Heading -->
          <tr>
            <td style="padding:16px 24px 0;text-align:center;">
              <div style="font-size:20px;font-weight:700;color:#0f172a;
                          line-height:1.3;">
                Your report {status_verb}
              </div>
            </td>
          </tr>

          <!-- Report details -->
          <tr>
            <td style="padding:20px 24px 0;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f8fafc;border-radius:10px;
                            border:1px solid #e2e8f0;">
                <tr>
                  <td style="padding:14px 16px;">
                    <div style="font-size:11px;font-weight:700;color:#94a3b8;
                                text-transform:uppercase;letter-spacing:0.08em;
                                margin-bottom:4px;">Report</div>
                    <div style="font-size:15px;font-weight:600;color:#0f172a;">
                      {title}
                    </div>
                    {"<div style='font-size:13px;color:#64748b;margin-top:3px;'>📍 " + location + "</div>" if location else ""}
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Council notes (if any) -->
          {notes_block}

          <!-- Footer message -->
          <tr>
            <td style="padding:24px 24px 0;text-align:center;">
              <p style="font-size:14px;color:#64748b;line-height:1.65;margin:0;">
                Thank you for taking the time to report this issue to your council.
                Your reports help make your community a better place.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px;text-align:center;border-top:1px solid #e2e8f0;
                       margin-top:24px;">
              <div style="font-size:12px;color:#94a3b8;">
                Local Lens &nbsp;·&nbsp; Community Issue Reporting
                {f"&nbsp;·&nbsp; Report #{report_id}" if report_id else ""}
              </div>
              <div style="font-size:11px;color:#cbd5e1;margin-top:4px;">
                This is an automated notification. Please do not reply to this email.
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, html_body


def _send(recipient: str, subject: str, html_body: str) -> bool:
    """Send the email via SMTP. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{_FROM_NAME} <{_SMTP_USER}>"
        msg["To"]      = recipient

        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()

        if _SMTP_PORT == 465:
            # SSL from the start
            with smtplib.SMTP_SSL(_SMTP_HOST, _SMTP_PORT, context=context) as server:
                server.login(_SMTP_USER, _SMTP_PASSWORD)
                server.sendmail(_SMTP_USER, recipient, msg.as_string())
        else:
            # STARTTLS (port 587 default)
            with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(_SMTP_USER, _SMTP_PASSWORD)
                server.sendmail(_SMTP_USER, recipient, msg.as_string())

        logger.info("Notification sent to %s (status: %s)", recipient, subject)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.warning(
            "SMTP authentication failed for %s. "
            "For Gmail, use an App Password not your account password.",
            _SMTP_USER,
        )
    except Exception as exc:
        logger.warning("Failed to send notification to %s: %s", recipient, exc)

    return False