# M2 Radar Activity Report Service

Automated monthly "Reporte de Actividad del M2" generation for Pronatura Noroeste A.C.

Downloads the Monthly Radar Track ZIP from the ProtectedSeas M2 API for each
configured radar site, parses the track attribute tables and hourly uptime data,
aggregates the month into a branded PDF report, and emails each PDF to that
site's recipient list. Includes a Flask + HTMX admin panel styled with the Pronatura
design system.

## Data source

The API token only has access to the download endpoints (the
`/external/historical` and photo endpoints return 403), so the pipeline uses:

```
GET /api/map/{radar_id}/{year}/{month:02d}/download-s3-zip
```

From the ZIP it reads `*_tracks_radar.dbf` + `*_tracks_ais.dbf` (track
attributes, parsed with a built-in pure-Python DBF reader — no GDAL needed)
and `*_radar_uptime.csv` (hourly component status → radar/AIS availability %
on the report). Timestamps in the ZIP are already in site-local time.

Counting rules match M2's own reporting: single-detection tracks
(`id_m2 IS NULL`) are excluded, and radar tracks strongly associated with an
AIS track (`assoc_str >= 20`) are dropped as duplicates.

## Radar sites

Seeded automatically on first boot: Loreto (23), Loreto 2 (42), San Basilio (45),
Islas Marías (48), El Pardito (55), Espíritu Santo (60).

## Quick start

```bash
cp .env.example .env       # fill in API token, SMTP credentials, admin password
docker compose up --build
```

Admin panel: http://localhost:5000/admin/ (HTTP Basic Auth, credentials from `.env`).

The scheduler runs all active sites on day `REPORT_RUN_DAY` (default: 2) of each
month at 06:00, reporting on the month that just ended.

## Admin panel

| Page | What it does |
|---|---|
| `/admin/` | One card per site: last run status, recipients, run-now |
| `/admin/sites/<id>` | Recipients CRUD, per-site history, manual trigger |
| `/admin/history` | Global report history, filterable by site |
| `/admin/settings` | SMTP connection test, YoY baseline editor |

While a run is in progress the dashboard polls `/admin/run/status` every 3 s
(HTMX) and updates each site card in place.

## Local development (without Docker)

WeasyPrint needs system libraries:

```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit values; set REPORT_OUTPUT_DIR/DATA_DIR to local paths
python -m app
```

## Tests

```bash
pip install pytest
pytest tests/
```

The aggregator tests run against fixture JSON and need no API token, network,
or WeasyPrint libraries.

## Project layout

```
app/
├── config.py        # .env loading + validation (SMTP_PORT cast to int here)
├── api/m2_client.py # ProtectedSeas API client, retry w/ backoff
├── pipeline/        # fetcher (API orchestration), aggregator (KPIs), chart_builder
├── report/          # Jinja2 template + WeasyPrint PDF generation
├── mailer/          # SMTP send with PDF attachment
├── scheduler/       # APScheduler cron + run_single_site shared entrypoint
├── admin/           # Flask blueprint, HTMX templates, Pronatura dashboard CSS
└── db/              # SQLAlchemy models, CRUD helpers, site seeding
```

## Operational notes

- **Re-runs overwrite**: one report per site per month; triggering the same
  period again replaces the record and PDF.
- **No recipients**: the PDF is generated and stored, the email step is skipped
  with a warning — not a failure.
- **Empty month** (radar downtime): report renders with zeroes and a note.
- **YoY baselines**: written automatically on each successful run; backfill
  pre-deployment history from the Settings page.
- **Photos**: best-effort. The photo endpoints currently return 403 for this
  token, so reports render without the photo section; if ProtectedSeas widens
  the token scope it starts working automatically (presigned URLs expire in
  1 hour, so bytes are downloaded immediately during fetch).
- **Radar downtime**: the report shows radar/AIS availability % from the
  uptime CSV. A zero-track month with low radar uptime is explained as
  equipment downtime, not absence of traffic (e.g. El Pardito, January 2026:
  radar offline all 744 hours).
