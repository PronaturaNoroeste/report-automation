"""Database read/write helpers.

Every function opens its own session so callers (scheduler thread, Flask
request handlers) never share session state across threads.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.db.models import RadarSite, Recipient, ReportRun, YoYBaseline

log = logging.getLogger(__name__)


# ---------------------------------------------------------------- RadarSite

def get_all_sites() -> list[RadarSite]:
    with SessionLocal() as s:
        return list(s.scalars(select(RadarSite).order_by(RadarSite.name)).all())


def get_active_sites() -> list[RadarSite]:
    with SessionLocal() as s:
        return list(
            s.scalars(
                select(RadarSite).where(RadarSite.active.is_(True)).order_by(RadarSite.name)
            ).all()
        )


def get_site(site_id: int) -> RadarSite | None:
    with SessionLocal() as s:
        return s.get(RadarSite, site_id)


def toggle_site_active(site_id: int) -> RadarSite | None:
    with SessionLocal() as s:
        site = s.get(RadarSite, site_id)
        if site is None:
            return None
        site.active = not site.active
        s.commit()
        return site


# ---------------------------------------------------------------- Recipient

def get_recipients(site_id: int) -> list[Recipient]:
    with SessionLocal() as s:
        return list(
            s.scalars(
                select(Recipient).where(Recipient.site_id == site_id).order_by(Recipient.name)
            ).all()
        )


def get_active_recipients(site_id: int) -> list[Recipient]:
    with SessionLocal() as s:
        return list(
            s.scalars(
                select(Recipient)
                .where(Recipient.site_id == site_id, Recipient.active.is_(True))
                .order_by(Recipient.name)
            ).all()
        )


def count_active_recipients(site_id: int) -> int:
    return len(get_active_recipients(site_id))


def add_recipient(site_id: int, name: str, email: str) -> Recipient | None:
    """Returns None if (site_id, email) already exists."""
    with SessionLocal() as s:
        exists = s.scalar(
            select(Recipient).where(Recipient.site_id == site_id, Recipient.email == email)
        )
        if exists:
            return None
        recipient = Recipient(site_id=site_id, name=name.strip(), email=email.strip().lower())
        s.add(recipient)
        s.commit()
        return recipient


def toggle_recipient(recipient_id: int) -> Recipient | None:
    with SessionLocal() as s:
        recipient = s.get(Recipient, recipient_id)
        if recipient is None:
            return None
        recipient.active = not recipient.active
        s.commit()
        return recipient


def delete_recipient(recipient_id: int) -> bool:
    with SessionLocal() as s:
        recipient = s.get(Recipient, recipient_id)
        if recipient is None:
            return False
        s.delete(recipient)
        s.commit()
        return True


# ---------------------------------------------------------------- ReportRun

def create_report_run(site_id: int, year: int, month: int, triggered_by: str) -> ReportRun:
    """Create or reset the run record for (site, year, month). Re-runs overwrite."""
    with SessionLocal() as s:
        run = s.scalar(
            select(ReportRun).where(
                ReportRun.site_id == site_id, ReportRun.year == year, ReportRun.month == month
            )
        )
        if run is None:
            run = ReportRun(site_id=site_id, year=year, month=month)
            s.add(run)
        run.status = "pending"
        run.triggered_by = triggered_by
        run.created_at = datetime.now(timezone.utc)
        run.error_message = None
        s.commit()
        return run


def update_report_run_success(run_id: int, kpis: dict, pdf_path: str) -> None:
    with SessionLocal() as s:
        run = s.get(ReportRun, run_id)
        run.status = "success"
        run.total_tracks = kpis["total_tracks"]
        run.alert_tracks = kpis["alert_tracks"]
        run.peak_alert_hour = kpis["peak_alert_hour"]
        run.busiest_weekday = kpis["busiest_weekday"]
        run.pdf_path = str(pdf_path)
        run.error_message = None
        s.commit()


def update_report_run_failed(site_id: int, year: int, month: int, error_message: str) -> None:
    with SessionLocal() as s:
        run = s.scalar(
            select(ReportRun).where(
                ReportRun.site_id == site_id, ReportRun.year == year, ReportRun.month == month
            )
        )
        if run is None:
            run = ReportRun(site_id=site_id, year=year, month=month)
            s.add(run)
        run.status = "failed"
        run.error_message = error_message[:2000]
        s.commit()


def get_report_run(run_id: int) -> ReportRun | None:
    with SessionLocal() as s:
        return s.get(ReportRun, run_id)


def get_site_history(site_id: int, limit: int = 24) -> list[ReportRun]:
    with SessionLocal() as s:
        return list(
            s.scalars(
                select(ReportRun)
                .where(ReportRun.site_id == site_id)
                .order_by(ReportRun.year.desc(), ReportRun.month.desc())
                .limit(limit)
            ).all()
        )


def get_global_history(site_id: int | None = None, limit: int = 100) -> list[ReportRun]:
    with SessionLocal() as s:
        stmt = select(ReportRun).order_by(ReportRun.created_at.desc()).limit(limit)
        if site_id is not None:
            stmt = stmt.where(ReportRun.site_id == site_id)
        runs = list(s.scalars(stmt).all())
        for run in runs:  # eager-load site names for templates
            _ = run.site.name
        return runs


def get_last_run(site_id: int) -> ReportRun | None:
    with SessionLocal() as s:
        return s.scalar(
            select(ReportRun)
            .where(ReportRun.site_id == site_id)
            .order_by(ReportRun.created_at.desc())
            .limit(1)
        )


# ---------------------------------------------------------------- YoYBaseline

def get_baseline(site_id: int, year: int, month: int) -> YoYBaseline | None:
    with SessionLocal() as s:
        return s.scalar(
            select(YoYBaseline).where(
                YoYBaseline.site_id == site_id,
                YoYBaseline.year == year,
                YoYBaseline.month == month,
            )
        )


def get_site_baselines(site_id: int) -> list[YoYBaseline]:
    with SessionLocal() as s:
        return list(
            s.scalars(
                select(YoYBaseline)
                .where(YoYBaseline.site_id == site_id)
                .order_by(YoYBaseline.year.desc(), YoYBaseline.month.desc())
            ).all()
        )


def save_yoy_baseline(site_id: int, year: int, month: int,
                      total_tracks: int, alert_tracks: int) -> YoYBaseline:
    with SessionLocal() as s:
        baseline = s.scalar(
            select(YoYBaseline).where(
                YoYBaseline.site_id == site_id,
                YoYBaseline.year == year,
                YoYBaseline.month == month,
            )
        )
        if baseline is None:
            baseline = YoYBaseline(site_id=site_id, year=year, month=month,
                                   total_tracks=total_tracks, alert_tracks=alert_tracks)
            s.add(baseline)
        else:
            baseline.total_tracks = total_tracks
            baseline.alert_tracks = alert_tracks
        s.commit()
        return baseline
