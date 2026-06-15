from datetime import date, datetime

import pytest

from app.db import crud
from app.pipeline.aggregator import WEEKDAY_ES, aggregate, compute_yoy


def track(dt: datetime | None, alarm: int = 0) -> dict:
    return {"id_track": 1, "id_m2": "x", "source": "radar", "local_dt": dt,
            "alarm": alarm, "has_photos": 0, "duration": 60, "max_speed": 5.0}


@pytest.fixture
def site():
    # San Basilio, seeded on init_db
    site = crud.get_site(45)
    assert site is not None
    return site


@pytest.fixture
def may_tracks():
    # 2026-05-01 is a Friday; 05-06, 05-13, 05-27 are Wednesdays
    all_tracks = [
        track(datetime(2026, 5, 1, 7, 10)),
        track(datetime(2026, 5, 1, 9, 30), alarm=1),
        track(datetime(2026, 5, 1, 18, 5)),
        track(datetime(2026, 5, 4, 12, 45)),
        track(datetime(2026, 5, 6, 6, 0), alarm=1),
        track(datetime(2026, 5, 6, 6, 25), alarm=1),
        track(datetime(2026, 5, 6, 15, 50)),
        track(datetime(2026, 5, 10, 8, 15)),
        track(datetime(2026, 5, 13, 6, 40), alarm=1),
        track(datetime(2026, 5, 20, 10, 0)),
        track(datetime(2026, 5, 27, 6, 10), alarm=1),
        track(datetime(2026, 5, 31, 16, 59)),
    ]
    return all_tracks, [t for t in all_tracks if t["alarm"]]


def test_aggregate_normal_month(site, may_tracks):
    all_tracks, alert_tracks = may_tracks
    kpis = aggregate(site, all_tracks, alert_tracks, 2026, 5,
                     uptime={"hours": 744, "online_pct": 98.0, "radar_pct": 97.2, "ais_pct": 100.0})

    assert kpis["total_tracks"] == 12
    assert kpis["alert_tracks"] == 5
    # 4 of 5 alerts fall in the 06:00 local hour
    assert kpis["peak_alert_hour"] == 6
    # 4 of 5 alerts on a Wednesday
    assert kpis["busiest_weekday"] == "Miércoles"
    assert kpis["month_name"] == "Mayo"
    assert kpis["days_in_month"] == 31

    assert kpis["daily_total"][date(2026, 5, 1)] == 3
    assert kpis["daily_total"][date(2026, 5, 6)] == 3
    assert sum(kpis["daily_total"].values()) == 12
    assert kpis["daily_alerts"][date(2026, 5, 6)] == 2

    assert kpis["radar_uptime_pct"] == 97.2
    assert kpis["ais_uptime_pct"] == 100.0

    # No baseline for 2025-05 → YoY omitted
    assert kpis["yoy_total_pct"] is None
    assert kpis["yoy_alert_pct"] is None


def test_aggregate_empty_month(site):
    kpis = aggregate(site, [], [], 2026, 2, uptime=None)

    assert kpis["total_tracks"] == 0
    assert kpis["alert_tracks"] == 0
    assert kpis["peak_alert_hour"] is None
    assert kpis["busiest_weekday"] is None
    assert kpis["daily_total"] == {}
    assert kpis["daily_alerts"] == {}
    assert kpis["radar_uptime_pct"] is None


def test_aggregate_with_yoy_baseline(may_tracks):
    # Use a different site than the other tests so the saved baseline
    # can't pollute their "no baseline → YoY is None" assertions.
    site = crud.get_site(23)  # Loreto
    all_tracks, alert_tracks = may_tracks
    crud.save_yoy_baseline(site.id, 2025, 5, total_tracks=10, alert_tracks=4)
    kpis = aggregate(site, all_tracks, alert_tracks, 2026, 5)

    assert kpis["yoy_total_pct"] == 20.0   # 10 → 12
    assert kpis["yoy_alert_pct"] == 25.0   # 4 → 5


def test_tracks_without_timestamps_do_not_crash(site):
    tracks = [track(None), track(None, alarm=1)]
    kpis = aggregate(site, tracks, [tracks[1]], 2026, 3)
    assert kpis["total_tracks"] == 2
    assert kpis["alert_tracks"] == 1
    assert kpis["daily_total"] == {}
    assert kpis["peak_alert_hour"] is None


def test_spillover_tracks_excluded(site):
    # The monthly ZIP can include tracks that started in the prior month
    tracks = [
        track(datetime(2026, 4, 30, 23, 50)),           # spillover → excluded
        track(datetime(2026, 5, 1, 0, 10), alarm=1),
        track(None),                                     # unknown start → kept
    ]
    kpis = aggregate(site, tracks, [tracks[1]], 2026, 5)
    assert kpis["total_tracks"] == 2
    assert kpis["alert_tracks"] == 1
    assert date(2026, 4, 30) not in kpis["daily_total"]


def test_compute_yoy():
    assert compute_yoy(120, 100) == 20.0
    assert compute_yoy(80, 100) == -20.0
    assert compute_yoy(5, 0) is None  # undefined vs. zero baseline
    assert compute_yoy(0, 50) == -100.0


def test_weekday_names_complete():
    assert set(WEEKDAY_ES.keys()) == set(range(7))
