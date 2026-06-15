"""Derive report KPIs from normalized track data.

Pure data transformation — no API calls. Unit-testable with fixture data.
Tracks arrive from the fetcher with `local_dt` already in site-local time
(the monthly ZIP reports sdate/stime locally), so no timezone math is needed.
Handles empty months (radar downtime) without crashing: zeroes + None KPIs.
"""

import calendar
import logging
from collections import Counter
from datetime import date

from app.db import crud
from app.db.models import RadarSite

log = logging.getLogger(__name__)

# Hardcoded Spanish names — avoids relying on an es_MX locale in the Docker image.
WEEKDAY_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo",
}

MONTH_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def compute_yoy(current: int, previous: int) -> float | None:
    """Percent change vs. previous year. None when previous is 0 (undefined)."""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


def _dts(tracks: list) -> list:
    return [t["local_dt"] for t in tracks if t.get("local_dt") is not None]


def _daily_counts(tracks: list) -> dict[date, int]:
    return dict(Counter(dt.date() for dt in _dts(tracks)))


def _in_month(track: dict, year: int, month: int) -> bool:
    """The monthly ZIP can include tracks that started in the prior month
    (spillover); count only tracks whose start date falls in the report month.
    Tracks without a parseable timestamp are kept — we can't prove them out.
    """
    dt = track.get("local_dt")
    return dt is None or (dt.year == year and dt.month == month)


def aggregate(site: RadarSite, all_tracks: list, alert_tracks: list,
              year: int, month: int, uptime: dict | None = None) -> dict:
    spillover = sum(1 for t in all_tracks if not _in_month(t, year, month))
    if spillover:
        log.info("[%s] excluding %d spillover tracks outside %d-%02d",
                 site.name, spillover, year, month)
    all_tracks = [t for t in all_tracks if _in_month(t, year, month)]
    alert_tracks = [t for t in alert_tracks if _in_month(t, year, month)]

    total_count = len(all_tracks)
    alert_count = len(alert_tracks)

    alert_dts = _dts(alert_tracks)
    if alert_dts:
        peak_hour = Counter(dt.hour for dt in alert_dts).most_common(1)[0][0]
        busiest_weekday_idx = Counter(dt.weekday() for dt in alert_dts).most_common(1)[0][0]
        busiest_weekday = WEEKDAY_ES[busiest_weekday_idx]
    else:
        peak_hour = None
        busiest_weekday = None

    # YoY against last year's same month — None on first deployment year.
    baseline = crud.get_baseline(site_id=site.id, year=year - 1, month=month)
    yoy_total_pct = compute_yoy(total_count, baseline.total_tracks) if baseline else None
    yoy_alert_pct = compute_yoy(alert_count, baseline.alert_tracks) if baseline else None

    return {
        "site": site,
        "year": year,
        "month": month,
        "month_name": MONTH_ES[month],
        "days_in_month": calendar.monthrange(year, month)[1],
        "total_tracks": total_count,
        "alert_tracks": alert_count,
        "peak_alert_hour": peak_hour,
        "busiest_weekday": busiest_weekday,
        "daily_total": _daily_counts(all_tracks),
        "daily_alerts": _daily_counts(alert_tracks),
        "yoy_total_pct": yoy_total_pct,
        "yoy_alert_pct": yoy_alert_pct,
        "radar_uptime_pct": uptime["radar_pct"] if uptime else None,
        "ais_uptime_pct": uptime["ais_pct"] if uptime else None,
    }
