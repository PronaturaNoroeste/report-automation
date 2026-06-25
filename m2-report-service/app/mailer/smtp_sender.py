"""Compose and send the monthly report email with PDF attachment."""

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.db.models import RadarSite, Recipient, ReportRun
from app.pipeline.aggregator import MONTH_ES

log = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "report" / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


def send_report(site: RadarSite, run: ReportRun, pdf_path: str,
                recipients: list[Recipient]) -> None:
    month_name = MONTH_ES[run.month]
    subject = f"Reporte de Actividad M2 — {site.name} — {month_name} {run.year}"
    template = _env.get_template("email_body.html")
    from_header = f"{settings.email_from_name} <{settings.smtp_user}>"
    filename = f"Reporte_M2_{site.slug}_{run.year}_{run.month:02d}.pdf"

    # Read the PDF once and reuse the bytes for every recipient.
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    sent = 0
    failed = 0
    # settings.smtp_port is already an int (cast in config.py)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=60) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)

        for recipient in recipients:
            body_html = template.render(
                site=site, run=run, month_name=month_name,
                recipient_name=recipient.name,
            )

            msg = MIMEMultipart("mixed")
            msg["Subject"] = subject
            msg["From"] = from_header
            msg["To"] = recipient.email  # plain address string — never a Recipient object
            msg.attach(MIMEText(body_html, "html"))

            attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            attachment.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(attachment)

            # One bad address shouldn't abort the rest of the batch.
            try:
                server.sendmail(settings.smtp_user, [recipient.email], msg.as_string())
                sent += 1
            except smtplib.SMTPException as e:
                failed += 1
                log.warning("[%s] Failed to email %s: %s", site.name, recipient.email, e)

    log.info("[%s] Report emailed to %d recipient(s), %d failed", site.name, sent, failed)


def test_smtp_connection() -> tuple[bool, str]:
    """Used by the admin settings page to verify SMTP credentials."""
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
        return True, "Conexión SMTP exitosa."
    except Exception as e:
        return False, f"Error de conexión SMTP: {e}"
