"""Admin panel routes — Flask Blueprint with HTMX partials.

Single admin account via HTTP Basic Auth. Manual report triggers run in a
background thread; the dashboard polls /admin/run/status while busy.
"""

import logging
import re
import secrets
import threading
from functools import wraps
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from app.config import settings
from app.db import crud
from app.pipeline.aggregator import MONTH_ES
from app.scheduler import jobs

log = logging.getLogger(__name__)

admin_bp = Blueprint(
    "admin", __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


# ------------------------------------------------------------------ auth

def _check_auth(username: str, password: str) -> bool:
    return secrets.compare_digest(username, settings.admin_username) and \
        secrets.compare_digest(password, settings.admin_password)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username or "", auth.password or ""):
            return Response(
                "Autenticación requerida.", 401,
                {"WWW-Authenticate": 'Basic realm="M2 Report Admin"'},
            )
        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------------ helpers

def _month_options() -> list[dict]:
    """Last 13 months (excluding the current one) for manual trigger selects."""
    options = []
    year, month = jobs.get_previous_month()
    for _ in range(13):
        options.append({
            "year": year, "month": month,
            "label": f"{MONTH_ES[month]} {year}",
            "value": f"{year}-{month:02d}",
        })
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return options


# Pragmatic single-address check; also guarantees no CR/LF (header injection)
# and no spaces. Not RFC-complete, but right for an operator-entered field.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email)) and len(email) <= 254


def _parse_period(raw: str) -> tuple[int, int]:
    year_s, month_s = raw.split("-", 1)
    year, month = int(year_s), int(month_s)
    if not 1 <= month <= 12:
        raise ValueError(f"Mes inválido: {month}")
    return year, month


def _site_cards() -> list[dict]:
    busy, states = jobs.run_tracker.snapshot()
    cards = []
    for site in crud.get_all_sites():
        last_run = crud.get_last_run(site.id)
        cards.append({
            "site": site,
            "last_run": last_run,
            "recipient_count": crud.count_active_recipients(site.id),
            "live": states.get(site.id),
        })
    return cards


def _trigger_in_background(sites, year: int, month: int) -> bool:
    """Start a batch in a daemon thread. Returns False if already busy."""
    busy, _ = jobs.run_tracker.snapshot()
    if busy:
        return False
    thread = threading.Thread(
        target=jobs.run_sites_batch,
        args=(sites, year, month, "manual"),
        daemon=True,
    )
    thread.start()
    return True


# ------------------------------------------------------------------ pages

@admin_bp.route("/")
@requires_auth
def dashboard():
    busy, _ = jobs.run_tracker.snapshot()
    return render_template(
        "dashboard.html",
        cards=_site_cards(),
        month_options=_month_options(),
        run_busy=busy,
        active_page="dashboard",
    )


@admin_bp.route("/sites/<int:site_id>")
@requires_auth
def site_detail(site_id: int):
    site = crud.get_site(site_id)
    if site is None:
        abort(404)
    busy, states = jobs.run_tracker.snapshot()
    return render_template(
        "site_detail.html",
        site=site,
        recipients=crud.get_recipients(site_id),
        history=crud.get_site_history(site_id),
        month_options=_month_options(),
        month_es=MONTH_ES,
        run_busy=busy,
        live=states.get(site_id),
        active_page=f"site-{site_id}",
    )


@admin_bp.route("/history")
@requires_auth
def history():
    site_id = request.args.get("site_id", type=int)
    return render_template(
        "history.html",
        runs=crud.get_global_history(site_id=site_id),
        sites=crud.get_all_sites(),
        selected_site_id=site_id,
        month_es=MONTH_ES,
        active_page="history",
    )


@admin_bp.route("/settings", methods=["GET", "POST"])
@requires_auth
def settings_page():
    if request.method == "POST":
        try:
            day = int(request.form["day"])
            hour, minute = (int(p) for p in request.form["time"].split(":"))
            if not (1 <= day <= 28 and 0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("fuera de rango")
            crud.set_schedule(day, hour, minute)
            jobs.reschedule_reports(day, hour, minute)
            flash("Programación de envío actualizada.", "success")
        except (KeyError, ValueError):
            flash("Datos inválidos: elija un día (1–28) y una hora.", "danger")
        return redirect(url_for("admin.settings_page"))

    day, hour, minute = crud.get_schedule()
    return render_template(
        "settings.html",
        day=day, hour=hour, minute=minute,
        next_run=jobs.next_report_run(),
        active_page="settings",
    )


# ------------------------------------------------------------------ recipients (HTMX)

@admin_bp.route("/sites/<int:site_id>/recipients/add", methods=["POST"])
@requires_auth
def add_recipient(site_id: int):
    name = request.form.get("name", "").strip()[:120]
    email = request.form.get("email", "").strip()
    error = None
    if not name or not _is_valid_email(email):
        error = "Nombre y correo válido son requeridos."
    elif crud.add_recipient(site_id, name, email) is None:
        error = "Ese correo ya está en la lista de este sitio."
    return render_template(
        "partials/recipient_list.html",
        site=crud.get_site(site_id),
        recipients=crud.get_recipients(site_id),
        error=error,
    )


@admin_bp.route("/sites/<int:site_id>/recipients/<int:recipient_id>/toggle", methods=["POST"])
@requires_auth
def toggle_recipient(site_id: int, recipient_id: int):
    recipient = crud.toggle_recipient(recipient_id)
    if recipient is None or recipient.site_id != site_id:
        abort(404)
    return render_template("partials/recipient_row.html", r=recipient, site_id=site_id)


@admin_bp.route("/sites/<int:site_id>/recipients/<int:recipient_id>/delete", methods=["DELETE"])
@requires_auth
def delete_recipient(site_id: int, recipient_id: int):
    crud.delete_recipient(recipient_id)
    return ""  # HTMX removes the row


# ------------------------------------------------------------------ triggers

@admin_bp.route("/sites/<int:site_id>/run", methods=["POST"])
@requires_auth
def run_site(site_id: int):
    site = crud.get_site(site_id)
    if site is None:
        abort(404)
    try:
        year, month = _parse_period(request.form.get("period", ""))
    except (ValueError, IndexError):
        flash("Periodo inválido.", "danger")
        return redirect(url_for("admin.site_detail", site_id=site_id))
    if _trigger_in_background([site], year, month):
        flash(f"Generando reporte de {site.name} para {MONTH_ES[month]} {year}…", "success")
    else:
        flash("Ya hay una ejecución en curso. Espere a que termine.", "warning")
    return redirect(url_for("admin.site_detail", site_id=site_id))


@admin_bp.route("/run/all", methods=["POST"])
@requires_auth
def run_all():
    try:
        year, month = _parse_period(request.form.get("period", ""))
    except (ValueError, IndexError):
        flash("Periodo inválido.", "danger")
        return redirect(url_for("admin.dashboard"))
    sites = crud.get_active_sites()
    if not sites:
        flash("No hay sitios activos.", "warning")
    elif _trigger_in_background(sites, year, month):
        flash(f"Generando reportes de {len(sites)} sitios para {MONTH_ES[month]} {year}…", "success")
    else:
        flash("Ya hay una ejecución en curso. Espere a que termine.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/run/status")
@requires_auth
def run_status():
    """HTMX-polled partial: refreshes the site cards while a batch is running."""
    busy, _ = jobs.run_tracker.snapshot()
    response = Response(render_template(
        "partials/site_cards.html",
        cards=_site_cards(),
        run_busy=busy,
    ))
    if not busy:
        # Tell the poller to stop (htmx stops on 286)
        response.status_code = 286
    return response


@admin_bp.route("/sites/<int:site_id>/toggle", methods=["POST"])
@requires_auth
def toggle_site(site_id: int):
    site = crud.toggle_site_active(site_id)
    if site is None:
        abort(404)
    flash(
        f"{site.name} {'incluido en' if site.active else 'excluido de'} las ejecuciones programadas.",
        "success",
    )
    return redirect(request.referrer or url_for("admin.dashboard"))


# ------------------------------------------------------------------ downloads

@admin_bp.route("/history/<int:run_id>/download")
@requires_auth
def download_report(run_id: int):
    run = crud.get_report_run(run_id)
    if run is None or not run.pdf_path or not Path(run.pdf_path).exists():
        abort(404)
    return send_file(run.pdf_path, as_attachment=True)
