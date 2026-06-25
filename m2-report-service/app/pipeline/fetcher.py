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
        "confidence": row.get("confidence"),  # radar detection confidence; None for AIS
        "ais_name": row.get("name"),          # AIS rows only
        "ais_type": row.get("type_m2"),       # AIS rows only
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
    tagged_rows: list[dict] = []
    uptime = None

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            lower = name.lower()
            if lower.endswith("tracks_radar_tagged.dbf"):
                tagged_rows = read_dbf(zf.read(name))
            elif lower.endswith("tracks_radar.dbf"):
                radar_rows = read_dbf(zf.read(name))
            elif lower.endswith("tracks_ais.dbf"):
                ais_rows = read_dbf(zf.read(name))
            elif lower.endswith("radar_uptime.csv"):
                uptime = parse_uptime_csv(zf.read(name).decode("utf-8-sig"))

    # Operator-review tags keyed by id_track. Absent/empty file → empty map.
    tag_map = {
        row["id_track"]: {"valid": row.get("valid"), "type": row.get("type")}
        for row in tagged_rows if row.get("id_track") is not None
    }

    tracks = [t for row in radar_rows if (t := normalize_track(row, "radar"))]
    for t in tracks:
        tag = tag_map.get(t["id_track"])
        if tag:
            t["tag_valid"] = tag["valid"]
            t["tag_type"] = tag["type"]
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

    alert_photo, alert_photo_caption = await _fetch_best_alert_photo(
        site.id, parsed["alert_tracks"]
    )

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
        "uptime": parsed["uptime"],                    # dict | None
        "alert_photo": alert_photo,                    # bytes | None
        "alert_photo_caption": alert_photo_caption,    # str | None
    }


def _score_alert_track(t: dict) -> float:
    """Rank a photo candidate by how confidently it shows a real, identifiable
    vessel. Higher wins. Pure signal already on the track — never excludes."""
    score = 0.0
    if t.get("tag_valid") and t.get("tag_type"):
        score += 100  # an operator reviewed it and recorded a vessel type
    if t.get("source") == "ais":
        score += 50   # broadcasts its own identity → definitely a real vessel
    conf = t.get("confidence")
    if isinstance(conf, (int, float)):
        score += conf  # radar detection confidence, as a tiebreaker
    return score


def _caption_for(t: dict) -> str | None:
    """Short caption identifying the vessel in the chosen photo, when known."""
    tag_type = (t.get("tag_type") or "").strip() if t.get("tag_valid") else ""
    if tag_type:
        return tag_type
    if t.get("source") == "ais":
        name = (t.get("ais_name") or "").strip()
        vtype = (t.get("ais_type") or "").strip()
        if name and vtype:
            return f"{name} — {vtype}"
        return name or vtype or None
    return None


async def _fetch_best_alert_photo(radar_id: int, alert_tracks: list,
                                  max_tracks: int = 5) -> tuple[bytes | None, str | None]:
    """Pick the photo most likely to show a real vessel: rank photo-bearing
    alert tracks by _score_alert_track and return the first that downloads,
    paired with an optional caption.

    The photos endpoint keys on id_track (the API's server_track_id), not id_m2.
    presigned_photo_url expires in 1 hour — bytes are downloaded immediately.

    Emits a one-line summary of where the search ended so an empty result is
    self-explaining in the logs (no alerts vs. none with photos vs. download
    failures).
    """
    photo_bearing = [t for t in alert_tracks if t.get("has_photos")]
    candidates = sorted(photo_bearing, key=_score_alert_track, reverse=True)[:max_tracks]

    lookups = photos_found = downloads = 0
    for track in candidates:
        track_id = track.get("id_track")
        if not track_id:
            continue
        lookups += 1
        photos = await m2_client.get_track_photos(radar_id, str(track_id))
        photos_found += len(photos)
        for photo in photos:
            url = photo.get("presigned_photo_url") or photo.get("url")
            if not url:
                continue
            downloads += 1
            photo_bytes = await m2_client.download_photo(url)
            if photo_bytes:
                caption = _caption_for(track)
                log.info("[radar %s] alert photo selected from track %s "
                         "(score=%.2f, caption=%r; %d/%d alert tracks carry photos)",
                         radar_id, track_id, _score_alert_track(track), caption,
                         len(photo_bearing), len(alert_tracks))
                return photo_bytes, caption

    log.info("[radar %s] no alert photo: %d alerts, %d with has_photos, "
             "%d lookups, %d photos found, %d downloads attempted",
             radar_id, len(alert_tracks), len(photo_bearing),
             lookups, photos_found, downloads)
    return None, None
