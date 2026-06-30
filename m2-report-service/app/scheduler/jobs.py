"""Monthly report job and shared per-site pipeline entrypoint.

`run_single_site()` is called by both the APScheduler cron job and the admin
panel's manual triggers. Both call sites wrap it in try/except — it raises on
failure so callers decide how to record the error.

`run_tracker` is an in-memory progress registry polled by the admin panel
(HTMX, every 3 s) while a run is in progress.
"""

import asyncio
import logging
import threading
import time
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db import crud
from app.db.models import RadarSite
from app.mailer import smtp_sender
from app.pipeline import aggregator, chart_builder, fetcher
from app.report import generator

log = logging.getLogger(__name__)

PAUSE_BETWEEN_SITES_SECONDS = 3


class RunTracker:
    """Thread-safe progress state for the admin panel's polling endpoint."""

    def __init__(self):
        self._lock = threading.Lock()
        self._states: dict[int, dict] = {}  # site_id -> {"status", "detail"}
        self._busy = False

    def start_batch(self, site_ids: list[int]) -> bool:
        """Mark a batch as started. Returns False if a run is already in progress."""
        with self._lock:
            if self._busy:
                return False
            self._busy = True
            self._states = {sid: {"status": "queued", "detail": ""} for sid in site_ids}
            return True

    def update(self, site_id: int, status: str, detail: str = "") -> None:
        with self._lock:
            self._states[site_id] = {"status": status, "detail": detail}

    def finish_batch(self) -> None:
        with self._lock:
            self._busy = False

    def snapshot(self) -> tuple[bool, dict[int, dict]]:
        with self._lock:
            return self._busy, {k: dict(v) for k, v in self._states.items()}


run_tracker = RunTracker()


def get_previous_month(today: date | None = None) -> tuple[int, int]:
    """The (year, month) of the month that just ended."""
    today = today or date.today()
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def run_single_site(site: RadarSite, year: int, month: int, triggered_by: str) -> None:
    """Full pipeline for one site: fetch → aggregate → chart → PDF → DB → email.

    Raises on failure; the caller records the failed status.
    """
    run = crud.create_report_run(site.id, year, month, triggered_by)
    run_tracker.update(site.id, "running", "Descargando paquete mensual…")

    data = asyncio.run(fetcher.fetch_site_monthly_data(site, year, month))

    run_tracker.update(site.id, "running", "Procesando datos…")
    kpis = aggregator.aggregate(site, data["all_tracks"], data["alert_tracks"], year, month,
                                uptime=data["uptime"])
    chart_png = chart_builder.build_daily_chart(
        kpis["daily_total"], kpis["daily_alerts"], year, month
    )

    run_tracker.update(site.id, "running", "Generando PDF…")
    pdf_path = generator.generate_pdf(kpis, chart_png)

    crud.update_report_run_success(run.id, kpis, pdf_path)
    crud.save_yoy_baseline(site.id, year, month, kpis["total_tracks"], kpis["alert_tracks"])
    run = crud.get_report_run(run.id)  # re-fetch: the email template needs the KPIs

    recipients = crud.get_active_recipients(site.id)
    if recipients:
        run_tracker.update(site.id, "running", "Enviando correo…")
        smtp_sender.send_report(site, run, pdf_path, recipients)
    else:
        log.warning("[%s] No active recipients — PDF generated but not sent.", site.name)

    run_tracker.update(site.id, "success", "Completado")


def run_sites_batch(sites: list[RadarSite], year: int, month: int, triggered_by: str) -> None:
    """Run a list of sites sequentially with a pause between them."""
    if not run_tracker.start_batch([s.id for s in sites]):
        log.warning("A report run is already in progress — skipping new batch.")
        return
    try:
        for site in sites:
            try:
                run_single_site(site, year, month, triggered_by)
            except Exception as e:
                log.exception("[%s] Failed: %s", site.name, e)
                crud.update_report_run_failed(site.id, year, month, str(e))
                run_tracker.update(site.id, "failed", str(e)[:200])
            finally:
                time.sleep(PAUSE_BETWEEN_SITES_SECONDS)
    finally:
        run_tracker.finish_batch()


def run_all_sites_job() -> None:
    """Scheduled entrypoint — reports on the month that just ended."""
    year, month = get_previous_month()
    sites = crud.get_active_sites()
    log.info("Monthly run starting: %d active sites, period %d-%02d", len(sites), year, month)
    run_sites_batch(sites, year, month, triggered_by="scheduler")


_JOB_ID = "monthly_report_all_sites"
_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    day, hour, minute = crud.get_schedule()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=run_all_sites_job,
        trigger=CronTrigger(day=day, hour=hour, minute=minute),
        id=_JOB_ID,
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    log.info("Scheduler started — monthly run on day %d at %02d:%02d", day, hour, minute)
    return scheduler


def reschedule_reports(day: int, hour: int, minute: int) -> None:
    """Apply a new global send schedule to the running scheduler (hot reload)."""
    if _scheduler is None:
        log.warning("reschedule_reports called before the scheduler started; skipping")
        return
    _scheduler.reschedule_job(_JOB_ID, trigger=CronTrigger(day=day, hour=hour, minute=minute))
    log.info("Reports rescheduled — monthly run on day %d at %02d:%02d", day, hour, minute)


def next_report_run():
    """Next scheduled run datetime (tz-aware) or None if not scheduled."""
    if _scheduler is None:
        return None
    job = _scheduler.get_job(_JOB_ID)
    return job.next_run_time if job else None
