"""Fetch and parse one site-month of data from the Monthly Radar Track ZIP.

The ZIP (see M2_ReadMe.pdf) contains, among others:
  {site}_{year}_{month}_tracks_radar.dbf   — radar track attributes
  {site}_{year}_{month}_tracks_ais.dbf    — AIS track attributes
  {site}_{year}_{month}_radar_uptime.csv  — hourly component status

Counting rules, chosen to match M2's own reporting:
  - tracks with NULL id_m2 (single-detection) are excluded — the README says
    they "are not considered in reporting";
  - radar tracks strongly associated with an AIS track (assoc_str >= 20) are
    excluded to avoid counting one vessel twice — 20 matched detections is
    the threshold M2 itself uses to suppress duplicates in the Viewer.

All sdate/stime values in the ZIP are already in site-local time.
"""

import csv
import io
import logging
import zipfile
from datetime import datetime

from app.api import m2_client
from app.db.models import RadarSite
from app.pipeline.dbf import read_dbf

log = logging.getLogger(__name__)

# Radar tracks with at least this many detections matched to an AIS track are
# treated as duplicates of that AIS track.
AIS_LINK_THRESHOLD = 20


# ------------------------------------------------------------------ parsing

def normalize_track(row: dict, source: str) -> dict | None:
    """Convert a raw DBF row into the aggregator's track shape, or None to skip."""
    if not row.get("id_m2"):
        return None  # single-detection track — not considered in reporting
    if source == "radar" and (row.get("assoc_str") or 0) >= AIS_LINK_THRESHOLD:
        return None  # duplicate of an AIS track

    local_dt = _parse_local_dt(row.get("sdate"), row.get("stime"))
    return {
        "id_track": row.get("id_track"),
        "id_m2": row.get("id_m2"),
        "source": source,
        "local_dt": local_dt,  # naive datetime in site-local time; may be None
        "alarm": int(row.get("alarm") or 0),
        "has_photos": int(row.get("has_photos") or 0),
        "duration": row.get("duration"),
        "max_speed": row.get("max_speed"),
    }


def _parse_local_dt(sdate, stime) -> datetime | None:
    if not sdate:
        return None
    try:
        date_part = str(sdate).strip()[:10]
        time_part = (str(stime).strip()[:8] if stime else "00:00:00") or "00:00:00"
        return datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        log.debug("Unparseable track timestamp: sdate=%r stime=%r", sdate, stime)
        return None


def parse_uptime_csv(text: str) -> dict | None:
    """Hourly status rows → uptime percentages. None if the file is empty."""
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        return None

    def pct(column: str) -> float:
        return round(100 * sum(1 for r in rows if r.get(column) == "1") / len(rows), 1)

    return {
        "hours": len(rows),
        "online_pct": pct("online"),
        "radar_pct": pct("radar_status"),
        "ais_pct": pct("ais_status"),
    }


def parse_monthly_zip(zip_bytes: bytes) -> dict:
    """Extract tracks and uptime from a monthly ZIP package."""
    radar_rows: list[dict] = []
    ais_rows: list[dict] = []
    uptime = None

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            lower = name.lower()
            if lower.endswith("tracks_radar.dbf"):
                radar_rows = read_dbf(zf.read(name))
            elif lower.endswith("tracks_ais.dbf"):
                ais_rows = read_dbf(zf.read(name))
            elif lower.endswith("radar_uptime.csv"):
                uptime = parse_uptime_csv(zf.read(name).decode("utf-8-sig"))

    tracks = [t for row in radar_rows if (t := normalize_track(row, "radar"))]
    tracks += [t for row in ais_rows if (t := normalize_track(row, "ais"))]
    alert_tracks = [t for t in tracks if t["alarm"]]

    return {
        "all_tracks": tracks,
        "alert_tracks": alert_tracks,
        "uptime": uptime,
        "raw_counts": {"radar": len(radar_rows), "ais": len(ais_rows)},
    }


# ------------------------------------------------------------------ fetch

async def fetch_site_monthly_data(site: RadarSite, year: int, month: int) -> dict:
    zip_bytes = await m2_client.download_monthly_zip(site.id, year, month)
    parsed = parse_monthly_zip(zip_bytes)

    alert_photo = await _fetch_first_alert_photo(site.id, parsed["alert_tracks"])

    log.info(
        "[%s] %d-%02d: %d tracks after filtering (raw radar=%d, ais=%d), "
        "%d alerts, radar uptime=%s%%, photo=%s",
        site.name, year, month,
        len(parsed["all_tracks"]),
        parsed["raw_counts"]["radar"], parsed["raw_counts"]["ais"],
        len(parsed["alert_tracks"]),
        parsed["uptime"]["radar_pct"] if parsed["uptime"] else "n/a",
        "yes" if alert_photo else "no",
    )

    return {
        "site": site,
        "all_tracks": parsed["all_tracks"],
        "alert_tracks": parsed["alert_tracks"],
        "uptime": parsed["uptime"],       # dict | None
        "alert_photo": alert_photo,       # bytes | None
    }


async def _fetch_first_alert_photo(radar_id: int, alert_tracks: list, max_tracks: int = 5) -> bytes | None:
    """Best-effort photo for the report. The photo endpoints currently return
    403 for this token; this degrades to None and starts working automatically
    if ProtectedSeas widens the token scope.

    presigned_photo_url expires in 1 hour — bytes are downloaded immediately.
    """
    candidates = [t for t in alert_tracks if t.get("has_photos")][:max_tracks]
    for track in candidates:
        track_id = track.get("id_track")
        if not track_id:
            continue
        photos = await m2_client.get_track_photos(radar_id, str(track_id))
        for photo in photos:
            url = photo.get("presigned_photo_url") or photo.get("url")
            if not url:
                continue
            photo_bytes = await m2_client.download_photo(url)
            if photo_bytes:
                return photo_bytes
    return None
