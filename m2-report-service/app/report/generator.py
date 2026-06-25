"""Render the monthly report: Jinja2 → HTML → WeasyPrint → PDF."""

import base64
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings

# WeasyPrint is imported lazily inside the render functions: importing it loads
# the Pango/Cairo C libraries, which keeps this module importable (for tests and
# tooling) on machines without those system packages.

log = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


def _b64(data: bytes | None) -> str | None:
    return base64.b64encode(data).decode("ascii") if data else None


def _static_b64(filename: str) -> str | None:
    """Inline a static asset (logo, radar photo) as base64, if present."""
    path = STATIC_DIR / filename
    if path.exists():
        return _b64(path.read_bytes())
    return None


def generate_pdf(kpis: dict, chart_png: bytes) -> str:
    from weasyprint import HTML

    site = kpis["site"]
    template = _env.get_template("monthly_report.html")

    html = template.render(
        site=site,
        kpis=kpis,
        chart_b64=_b64(chart_png),
        logo_b64=_static_b64("pronatura_logo.png"),
        radar_photo_b64=_static_b64("radar_tower.jpg"),
    )

    out_dir = settings.report_output_dir / site.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{kpis['year']}_{kpis['month']:02d}_{site.slug}.pdf"

    HTML(string=html, base_url=str(STATIC_DIR)).write_pdf(str(pdf_path))
    log.info("[%s] PDF written to %s", site.name, pdf_path)
    return str(pdf_path)


def startup_check() -> None:
    """Render a minimal one-page PDF to confirm WeasyPrint's system deps work.

    Called once on boot; raises with a clear message if the stack is broken.
    """
    try:
        from weasyprint import HTML

        HTML(string="<h1>WeasyPrint OK</h1>").write_pdf()
    except Exception as e:
        raise RuntimeError(
            "WeasyPrint startup check failed — are libpango/libcairo installed? "
            f"Original error: {e}"
        ) from e
