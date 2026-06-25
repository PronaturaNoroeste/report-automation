"""Tests for the ZIP-based data path.

Uses two sources:
  1. The real El Pardito 2026-01 sample (radar offline all month, 0 tracks) —
     exercises the empty-month/downtime path with production data.
  2. A synthetic DBF written in-test — exercises parsing of populated files,
     including the reporting filters (NULL id_m2, AIS-linked radar tracks).
"""

import io
import struct
import zipfile
from datetime import datetime
from pathlib import Path

from app.pipeline.dbf import read_dbf
from app.pipeline.fetcher import (
    AIS_LINK_THRESHOLD,
    normalize_track,
    parse_monthly_zip,
    parse_uptime_csv,
)

SAMPLE_DIR = Path(__file__).parent / "fixtures" / "55_2026_01"


# ------------------------------------------------------------- DBF writer

def write_dbf(fields: list[tuple[str, str, int]], rows: list[dict]) -> bytes:
    """Minimal dBase III writer for test fixtures."""
    record_size = 1 + sum(length for _, _, length in fields)
    header_size = 32 + 32 * len(fields) + 1

    out = bytearray()
    out += struct.pack("<BBBBIHH20x", 0x03, 26, 1, 1, len(rows), header_size, record_size)
    for name, ftype, length in fields:
        out += name.encode("ascii").ljust(11, b"\0")
        out += ftype.encode("ascii")
        out += b"\0" * 4 + bytes([length]) + b"\0" * 15
    out += b"\x0D"

    for row in rows:
        out += b" "  # not deleted
        for name, ftype, length in fields:
            value = row.get(name)
            text = "" if value is None else str(value)
            if ftype == "N":
                out += text.rjust(length)[:length].encode("ascii")
            else:
                out += text.ljust(length)[:length].encode("latin-1")
    out += b"\x1a"
    return bytes(out)


TRACK_FIELDS = [
    ("id_track", "N", 11), ("id_m2", "C", 30), ("alarm", "N", 4),
    ("assoc_str", "N", 11), ("has_photos", "N", 4), ("duration", "N", 11),
    ("max_speed", "N", 10), ("sdate", "C", 30), ("stime", "C", 39),
]


def make_track_row(id_track, id_m2, sdate, stime, alarm=0, assoc_str=None, has_photos=0):
    return {"id_track": id_track, "id_m2": id_m2, "alarm": alarm,
            "assoc_str": assoc_str, "has_photos": has_photos,
            "duration": 120, "max_speed": 8.5, "sdate": sdate, "stime": stime}


# ------------------------------------------------------------- real sample

def test_real_sample_dbf_schemas():
    rows = read_dbf((SAMPLE_DIR / "55_2026_01_tracks_radar.dbf").read_bytes())
    assert rows == []  # radar offline all of January 2026
    rows = read_dbf((SAMPLE_DIR / "55_2026_01_tracks_ais.dbf").read_bytes())
    assert rows == []


def test_real_sample_uptime():
    uptime = parse_uptime_csv((SAMPLE_DIR / "55_2026_01_radar_uptime.csv").read_text())
    assert uptime["hours"] == 744          # 31 days × 24
    assert uptime["radar_pct"] == 0.0      # radar down the whole month
    assert uptime["online_pct"] == 0.0
    assert uptime["ais_pct"] == 100.0      # AIS receiver stayed up


def test_real_sample_as_zip_empty_month():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for f in SAMPLE_DIR.iterdir():
            zf.write(f, arcname=f.name)
    parsed = parse_monthly_zip(buffer.getvalue())

    assert parsed["all_tracks"] == []
    assert parsed["alert_tracks"] == []
    assert parsed["uptime"]["radar_pct"] == 0.0
    assert parsed["raw_counts"] == {"radar": 0, "ais": 0}


# ------------------------------------------------------------- synthetic data

def test_parse_populated_zip_with_filters():
    radar_rows = [
        make_track_row(1, "55-0501-0001", "2026-05-01", "09:30:00", alarm=1),
        make_track_row(2, "55-0501-0002", "2026-05-01", "14:00:00"),
        # single-detection track: NULL id_m2 → excluded from reporting
        make_track_row(3, None, "2026-05-02", "10:00:00"),
        # strongly AIS-linked radar track → excluded as duplicate
        make_track_row(4, "55-0503-0004", "2026-05-03", "11:00:00",
                       assoc_str=AIS_LINK_THRESHOLD),
        # weakly associated → kept
        make_track_row(5, "55-0503-0005", "2026-05-03", "12:00:00",
                       assoc_str=AIS_LINK_THRESHOLD - 1),
    ]
    ais_rows = [
        make_track_row(10, "367104050-0504-0900", "2026-05-04", "09:00:00",
                       alarm=1, has_photos=1),
    ]
    uptime_csv = (
        "\"id_site\",\"online\",\"radar_status\",\"ais_status\",\"cdate\",\"ctime\"\n"
        + "\n".join(f'55,1,{1 if i % 4 else 0},1,2026-05-01,{i:02d}:00:00' for i in range(24))
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("55_2026_05_tracks_radar.dbf", write_dbf(TRACK_FIELDS, radar_rows))
        zf.writestr("55_2026_05_tracks_ais.dbf", write_dbf(TRACK_FIELDS, ais_rows))
        zf.writestr("55_2026_05_radar_uptime.csv", uptime_csv)
        zf.writestr("M2_ReadMe.pdf", b"%PDF-fake")

    parsed = parse_monthly_zip(buffer.getvalue())

    assert parsed["raw_counts"] == {"radar": 5, "ais": 1}
    assert len(parsed["all_tracks"]) == 4          # 3 radar kept + 1 ais
    assert len(parsed["alert_tracks"]) == 2
    kept_ids = {t["id_track"] for t in parsed["all_tracks"]}
    assert kept_ids == {1, 2, 5, 10}

    ais_track = next(t for t in parsed["all_tracks"] if t["source"] == "ais")
    assert ais_track["local_dt"] == datetime(2026, 5, 4, 9, 0)
    assert ais_track["has_photos"] == 1

    assert parsed["uptime"]["hours"] == 24
    assert parsed["uptime"]["radar_pct"] == 75.0   # 18 of 24 hours


def test_normalize_track_handles_bad_timestamp():
    row = make_track_row(7, "55-x", "not-a-date", "99:99:99")
    t = normalize_track(row, "radar")
    assert t is not None
    assert t["local_dt"] is None
