from datetime import date

from app.config import settings
from app.db import crud
from app.db.seed import RADAR_SITES, seed_radar_sites
from app.scheduler.jobs import get_previous_month


def test_smtp_port_is_int():
    assert isinstance(settings.smtp_port, int)
    assert settings.smtp_port == 587


def test_seed_is_idempotent():
    seed_radar_sites()
    seed_radar_sites()
    sites = crud.get_all_sites()
    assert len(sites) == len(RADAR_SITES)
    assert {s.id for s in sites} == {23, 42, 45, 48, 55, 60}


def test_get_previous_month():
    assert get_previous_month(date(2026, 6, 2)) == (2026, 5)
    assert get_previous_month(date(2026, 1, 2)) == (2025, 12)


def test_chart_builder_returns_png():
    from app.pipeline.chart_builder import build_daily_chart

    png = build_daily_chart({date(2026, 5, 1): 3}, {date(2026, 5, 1): 1}, 2026, 5)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_recipient_unique_per_site():
    crud.add_recipient(23, "Test", "dup@example.test")
    assert crud.add_recipient(23, "Test again", "dup@example.test") is None
    # Same email allowed on a different site
    assert crud.add_recipient(42, "Test", "dup@example.test") is not None
