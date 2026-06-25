"""Tests for alert-photo selection: ranking, captions, tag join, and fetch.

Guards behaviour confirmed live against radar 23 (photos endpoint keys on
id_track) and the design in
docs/superpowers/specs/2026-06-25-alert-photo-vessel-ranking-design.md:
any photo-bearing alert track is a valid candidate (no all-excluding filter),
but the highest "real vessel" score is preferred.
"""

import asyncio

from app.pipeline import fetcher
from app.pipeline.fetcher import (
    _caption_for,
    _fetch_best_alert_photo,
    _score_alert_track,
)


def track(id_track, has_photos=1, **over):
    t = {"id_track": id_track, "has_photos": has_photos, "source": "radar"}
    t.update(over)
    return t


def make_client(monkeypatch, photo_tracks, *, bytes_for=None):
    """Stub m2_client: get_track_photos yields a URL for ids in photo_tracks;
    download_photo returns bytes for ids in bytes_for (default: all)."""
    queried = []

    async def fake_get_track_photos(radar_id, track_id):
        queried.append(track_id)
        if int(track_id) in photo_tracks:
            return [{"presigned_photo_url": f"https://x/{track_id}.jpg"}]
        return []

    async def fake_download_photo(url):
        tid = int(url.rsplit("/", 1)[1].split(".")[0])
        if bytes_for is None or tid in bytes_for:
            return b"\xff\xd8JPEG"
        return None

    monkeypatch.setattr(fetcher.m2_client, "get_track_photos", fake_get_track_photos)
    monkeypatch.setattr(fetcher.m2_client, "download_photo", fake_download_photo)
    return queried


# ------------------------------------------------------------- scoring

def test_score_orders_tagged_over_ais_over_plain():
    tagged = track(1, tag_valid=1, tag_type="Pesca")
    ais = track(2, source="ais")
    plain = track(3)
    assert _score_alert_track(tagged) > _score_alert_track(ais) > _score_alert_track(plain)


def test_score_confidence_breaks_ties():
    lo = track(1, confidence=0.2)
    hi = track(2, confidence=0.9)
    assert _score_alert_track(hi) > _score_alert_track(lo)


def test_score_tag_needs_both_valid_and_type():
    # valid flag without a type, or a type that wasn't marked valid, earns no bonus.
    assert _score_alert_track(track(1, tag_valid=1)) == 0.0
    assert _score_alert_track(track(2, tag_type="Pesca")) == 0.0


# ------------------------------------------------------------- captions

def test_caption_prefers_operator_tag_type():
    assert _caption_for(track(1, tag_valid=1, tag_type="Embarcación de pesca")) \
        == "Embarcación de pesca"


def test_caption_uses_ais_name_and_type():
    t = track(2, source="ais", ais_name="DON JULIO", ais_type="Fishing")
    assert _caption_for(t) == "DON JULIO — Fishing"


def test_caption_none_for_plain_track():
    assert _caption_for(track(3)) is None
    # tagged-but-not-valid earns no caption either
    assert _caption_for(track(4, tag_type="Pesca")) is None


# ------------------------------------------------------------- selection

def test_picks_highest_scored_downloadable(monkeypatch):
    queried = make_client(monkeypatch, photo_tracks={10, 11, 12})
    tracks = [
        track(10),                                   # plain
        track(11, source="ais"),                     # mid
        track(12, tag_valid=1, tag_type="Pesca"),    # best
    ]
    photo, caption = asyncio.run(_fetch_best_alert_photo(23, tracks))
    assert photo == b"\xff\xd8JPEG"
    assert caption == "Pesca"
    assert queried == ["12"]  # best-scored queried first and won


def test_any_photo_track_qualifies_no_filter(monkeypatch):
    """A lone plain alert with wild kinematics still yields a photo (no caption).
    Guards against silently reintroducing an all-excluding filter."""
    make_client(monkeypatch, photo_tracks={40})
    weird = track(40, max_speed=999, confidence=None, distance=9999)
    photo, caption = asyncio.run(_fetch_best_alert_photo(23, [weird]))
    assert photo == b"\xff\xd8JPEG"
    assert caption is None


def test_falls_through_when_best_download_fails(monkeypatch):
    # Best-scored (61, tagged) fails to download; falls to AIS (60).
    queried = make_client(monkeypatch, photo_tracks={60, 61}, bytes_for={60})
    tracks = [track(60, source="ais"), track(61, tag_valid=1, tag_type="Pesca")]
    photo, caption = asyncio.run(_fetch_best_alert_photo(23, tracks))
    assert photo == b"\xff\xd8JPEG"
    assert caption is None            # came from the AIS track, no name/type
    assert queried == ["61", "60"]    # tried best first, then fell through


def test_returns_none_tuple_when_no_photo_tracks(monkeypatch):
    async def boom(*a, **k):
        raise AssertionError("should not query when no track has has_photos")

    monkeypatch.setattr(fetcher.m2_client, "get_track_photos", boom)
    assert asyncio.run(_fetch_best_alert_photo(23, [track(50, has_photos=0)])) == (None, None)
