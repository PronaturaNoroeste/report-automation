# Alert-Photo Vessel Ranking — Design

Date: 2026-06-25
Status: Draft for review

## Background

The monthly report features one "alert photo" pulled from the M2 photo
endpoint. Today `_fetch_first_alert_photo` takes the **first** photo-bearing
alert track that downloads — no notion of whether the frame actually shows a
real vessel. The camera fires on radar detection, so a frame can be empty
water, glare, wake, or a bird.

A prior attempt filtered alert tracks by kinematic thresholds
(confidence/speed/distance). That was removed: it judged *motion*, not image
content, and (AND-ed, plus excluding AIS tracks) silently zeroed out the
candidate set → "no photo at all". See
`memory/photo-endpoint-userid.md`.

Confirmed live (radar 23, 2026-04): the photos endpoint keys on `id_track`
(HTTP 200 + `presigned_photo_url`); `id_m2` → 404. The fetch is healthy; this
work is about *which* photo we choose, not whether one returns.

## Goal

Choose the featured photo more likely to show a **real, identifiable vessel**,
and caption it when we know what it is — without shrinking the result to zero
on thin months.

## Non-Goals

- No change to scope: the photo still comes from **alert tracks** (`alarm=1`).
- Still exactly **one** photo (no grid/gallery).
- No broadening to non-alert tracks, no vision model.

## Design

### Selection: rank, don't take-first

Replace "first photo-bearing alert track wins" with a ranked pick. For each
photo-bearing alert track compute a **real-vessel score** (higher = preferred):

| Signal | Points | Source |
|--------|--------|--------|
| Operator-tagged `valid` with a `type` | +100 | `tracks_radar_tagged.dbf` |
| AIS-source track (broadcasts identity) | +50 | `source == "ais"` (already parsed) |
| Detection `confidence` (0–1) | + value | radar DBF (tiebreaker) |

Iterate candidates in descending score; return the first whose photo
downloads. Behaviour with no candidates is unchanged (returns `None`, report
omits the photo). The existing `max_tracks` cap still bounds API calls, applied
to the ranked order.

### Caption (bonus output)

Derive an optional short caption for the chosen photo:

1. Operator tag `type` (e.g. "Embarcación de pesca") — preferred.
2. AIS vessel `name` / `type_m2` when the track is AIS-source.
3. Otherwise `None` (no caption rendered).

Captions are Spanish, matching the report.

### Reading the tagged DBF

`parse_monthly_zip` already reads `*_tracks_radar.dbf` and `*_tracks_ais.dbf`.
Add `*_tracks_radar_tagged.dbf`: parse it into a map `id_track -> {valid, type}`
and attach `tag_valid` / `tag_type` onto matching radar tracks during
normalization (join on `id_track`). Tagged file absent or empty → tracks simply
carry no tag fields (graceful).

AIS name/type: carry `name` and `type_m2` through `normalize_track` for AIS
rows so captions can use them.

### Data flow / touch points

- `fetcher.py`
  - `parse_monthly_zip`: read the tagged DBF, build the tag map, join onto radar tracks.
  - `normalize_track`: carry `confidence` (radar), `name`/`type_m2` (AIS), and joined `tag_valid`/`tag_type`.
  - new `_score_alert_track(track) -> float` and `_caption_for(track) -> str | None`.
  - `_fetch_first_alert_photo`: rank candidates by score; return `(bytes, caption)` or `(None, None)`.
  - `fetch_site_monthly_data` returns `alert_photo` and `alert_photo_caption`.
- `report/generator.py`: `generate_pdf(..., alert_photo, alert_photo_caption)`.
- `report/templates/monthly_report.html`: render caption under the photo (`{% if alert_photo_caption %}`).
- `scheduler/jobs.py`: pass the caption through.

### Error handling / graceful degradation

- Tagged DBF missing/empty → no tag signal, ranking falls back to AIS + confidence.
- No photo-bearing alert track → `None`, report omits photo (unchanged).
- Caption absent → photo renders without a caption (unchanged layout).

### Testing

- `_score_alert_track`: tagged-valid > AIS > plain; confidence tiebreaker.
- `_caption_for`: tag type, AIS name/type, None fallback.
- tagged-DBF join: tag fields land on the right `id_track`; absent file is safe.
- `_fetch_first_alert_photo` (mocked client): picks the highest-scored
  downloadable candidate; still returns a photo when only a plain alert exists;
  returns `(None, None)` when none have photos.

## Open decision (cut line)

The `tracks_radar_tagged.dbf` read + captions are the bulk of the work and
depend on operators actually tagging. If we want minimal: rank on **AIS-source +
confidence only** (no new DBF), and drop captions (or AIS-only captions). The
selection improvement still lands; only operator-tag richness is lost.

## Rollout

Code change only; same container. Rebuild + `docker compose up -d` (batched
with the Phase-0 logging already added but not yet shipped to the running
image).
