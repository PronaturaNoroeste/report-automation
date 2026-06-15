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
    body_html = _env.get_template("email_body.html").render(
        site=site, run=run, month_name=month_name
    )
    # Plain address strings — never Recipient objects.
    to_addresses = [r.email for r in recipients]

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"{settings.email_from_name} <{settings.smtp_user}>"
    msg["To"] = ", ".join(to_addresses)
    msg.attach(MIMEText(body_html, "html"))

    filename = f"Reporte_M2_{site.slug}_{run.year}_{run.month:02d}.pdf"
    with open(pdf_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    # settings.smtp_port is already an int (cast in config.py)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=60) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, to_addresses, msg.as_string())

    log.info("[%s] Report emailed to %d recipient(s)", site.name, len(to_addresses))


def test_smtp_connection() -> tuple[bool, str]:
    """Used by the admin settings page to verify SMTP credentials."""
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
        return True, "Conexión SMTP exitosa."
    except Exception as e:
        return False, f"Error de conexión SMTP: {e}"
