# M2 Radar Activity Report — Automation Service Architecture

**Project:** Monthly Radar Activity Report Automation — Multi-Site  
**Client:** Pronatura Noroeste A.C.  
**Handoff target:** Claude Code  
**Last updated:** June 2026

---

## 1. Overview

A standalone Python service that runs on a monthly schedule, pulls vessel tracking data from the ProtectedSeas M2 API for all configured radar sites, aggregates each into a human-readable PDF report (matching the established Reporte de Actividad del M2 format), and dispatches each PDF to that site's recipient list via SMTP. An admin panel (Flask + HTMX) allows Pronatura staff to manage sites, per-site recipient lists, view report history per site, manually trigger runs per site or all at once, and configure year-over-year baseline data per site.

---

## 2. Radar Site Registry

These are the only radar IDs the API token has access to. They are seeded into the database on first boot — not stored in `.env`.

| Site Name | Radar ID |
|---|---|
| Loreto | 23 |
| Loreto 2 | 42 |
| San Basilio | 45 |
| Islas Marías | 48 |
| El Pardito | 55 |
| Espíritu Santo | 60 |

---

## 3. Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Language | Python 3.12 | Already in use at Pronatura; no new runtime |
| Scheduling | APScheduler (in-process) | One monthly cron job iterates all sites sequentially; no Celery/Redis needed |
| API Client | `httpx` (async) | Clean async HTTP with retry logic |
| Data Processing | `pandas` | Bucketing tracks by day/hour/weekday per site |
| Chart Generation | `matplotlib` | Produces "Tracks Over Date Range" time-series chart per site |
| PDF Generation | `WeasyPrint` | HTML → PDF with full CSS control; matches branded report layout |
| Report Template | `Jinja2` | HTML template rendered before WeasyPrint pass; site name injected dynamically |
| Admin Panel | `Flask` + `HTMX` | Lightweight server-rendered UI; no frontend build step |
| Database | `SQLite` (via `SQLAlchemy`) | Stores sites, per-site recipients, report history, YoY baselines |
| Email Dispatch | `smtplib` (stdlib) + `email` | Works with any SMTP relay (Gmail, Mailgun, etc.) |
| Config | `python-dotenv` + `.env` | Secrets never in code |
| Containerization | `Docker` + `docker-compose` | Single `docker compose up` to run everything |

---

## 4. Project Structure

```
m2-report-service/
│
├── app/
│   ├── __init__.py
│   ├── config.py                   # Loads .env, validates required vars
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── m2_client.py            # All ProtectedSeas M2 API calls
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── fetcher.py              # Orchestrates API calls for a given site + month
│   │   ├── aggregator.py           # Derives KPIs from raw track data
│   │   └── chart_builder.py        # Generates matplotlib chart as PNG bytes
│   │
│   ├── report/
│   │   ├── __init__.py
│   │   ├── generator.py            # Renders Jinja2 template → WeasyPrint PDF
│   │   └── templates/
│   │       ├── monthly_report.html # Branded HTML template; site name dynamic
│   │       └── email_body.html     # Email body template
│   │
│   ├── mailer/
│   │   ├── __init__.py
│   │   └── smtp_sender.py          # Composes and sends email with PDF attachment
│   │
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── jobs.py                 # Single cron job; iterates all active sites
│   │
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py               # Flask Blueprint: all admin panel routes
│   │   └── templates/
│   │       ├── base.html
│   │       ├── dashboard.html      # All-sites overview; last run status per site
│   │       ├── site_detail.html    # Per-site: recipients, history, manual trigger
│   │       ├── history.html        # Global report history across all sites
│   │       └── settings.html       # SMTP config, YoY baselines per site/month
│   │
│   └── db/
│       ├── __init__.py
│       ├── models.py               # SQLAlchemy models
│       ├── crud.py                 # DB read/write helpers
│       └── seed.py                 # Seeds RadarSite rows on first boot
│
├── reports/                        # Generated PDFs saved here (volume-mounted)
│   ├── loreto/
│   ├── loreto_2/
│   ├── san_basilio/
│   ├── islas_marias/
│   ├── el_pardito/
│   └── espiritu_santo/
├── logs/
├── .env.example
├── .env                            # NOT committed
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 5. Environment Variables (`.env`)

```dotenv
# ProtectedSeas M2 API
M2_API_BASE_URL=https://m2mobile.protectedseas.net/api/map
M2_API_TOKEN=your_token_here
M2_USER_ID=your_user_id_here        # For photo endpoints — same token covers all sites

# Email / SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587                       # Cast to int() at load time — do not leave as string
SMTP_USER=reports@pronatura-noroeste.org
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM_NAME=Monitor Marino Pronatura Noroeste

# Admin Panel
ADMIN_SECRET_KEY=change_this_to_a_long_random_string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_too

# Service
REPORT_OUTPUT_DIR=/app/reports
LOG_LEVEL=INFO

# Scheduler — day of month to run all site reports (default: 2)
REPORT_RUN_DAY=2
```

---

## 6. Database Models (`app/db/models.py`)

### `RadarSite`
Seeded on first boot. One row per site. Admin panel can toggle `active`.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Matches the M2 API radar_id exactly |
| `name` | VARCHAR | Display name (e.g., "San Basilio") |
| `slug` | VARCHAR UNIQUE | URL-safe identifier (e.g., `san_basilio`); used for PDF subdirectory |
| `timezone` | VARCHAR | IANA tz string (e.g., `America/Mazatlan`) |
| `active` | BOOLEAN | Whether to include in monthly scheduled run |
| `added_at` | DATETIME | Timestamp |

**Seed data:**
```python
RADAR_SITES = [
    {"id": 23, "name": "Loreto",          "slug": "loreto",          "timezone": "America/Mazatlan"},
    {"id": 42, "name": "Loreto 2",        "slug": "loreto_2",        "timezone": "America/Mazatlan"},
    {"id": 45, "name": "San Basilio",     "slug": "san_basilio",     "timezone": "America/Mazatlan"},
    {"id": 48, "name": "Islas Marías",    "slug": "islas_marias",    "timezone": "America/Mazatlan"},
    {"id": 55, "name": "El Pardito",      "slug": "el_pardito",      "timezone": "America/Mazatlan"},
    {"id": 60, "name": "Espíritu Santo",  "slug": "espiritu_santo",  "timezone": "America/Mazatlan"},
]
```

> **Note for Claude Code:** Verify the correct IANA timezone for each site before seeding. All sites are in Baja California Sur / Sinaloa — likely `America/Mazatlan` (UTC-7, no DST) or `America/Hermosillo`. Confirm with Pronatura if unsure.

---

### `Recipient`
Per-site mailing list. Each recipient belongs to exactly one site.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `site_id` | INTEGER FK → RadarSite.id | Which site this recipient belongs to |
| `name` | VARCHAR | Display name |
| `email` | VARCHAR | Email address |
| `active` | BOOLEAN | Whether to include in next send for this site |
| `added_at` | DATETIME | Timestamp |

**Unique constraint:** `(site_id, email)` — same email can be on multiple site lists but not duplicated within one site.

---

### `ReportRun`
One row per site per month per run attempt.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `site_id` | INTEGER FK → RadarSite.id | Which site this report covers |
| `year` | INTEGER | Report year |
| `month` | INTEGER | Report month (1–12) |
| `status` | VARCHAR | `pending`, `success`, `failed` |
| `total_tracks` | INTEGER | KPI from API |
| `alert_tracks` | INTEGER | KPI from API |
| `peak_alert_hour` | INTEGER | Derived (0–23) |
| `busiest_weekday` | VARCHAR | Derived (e.g., "Miércoles") |
| `pdf_path` | VARCHAR | Absolute path to generated PDF |
| `triggered_by` | VARCHAR | `scheduler` or `manual` |
| `created_at` | DATETIME | Timestamp of run |
| `error_message` | TEXT | Null on success |

**Unique constraint:** `(site_id, year, month)` — one successful report per site per month. A re-run overwrites the existing record.

---

### `YoYBaseline`
Prior-year KPIs per site per month. Written automatically on each successful run.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto |
| `site_id` | INTEGER FK → RadarSite.id | Which site |
| `year` | INTEGER | The year these numbers apply to |
| `month` | INTEGER | Month (1–12) |
| `total_tracks` | INTEGER | Historical total track count |
| `alert_tracks` | INTEGER | Historical alert count |
| `updated_at` | DATETIME | Last edit timestamp |

**Unique constraint:** `(site_id, year, month)`

---

## 7. API Endpoints Used

Same 3 calls as before, now parameterized per site. The same API token covers all 6 radar IDs.

### Call 1 — All Monthly Tracks (per site)
```
GET /api/map/external/historical/{radar_id}/{start_unix}/{end_unix}/{tzi}/
    ?limit=10000&page=1
```

### Call 2 — Alarmed Tracks Only (per site)
```
GET /api/map/external/historical/{radar_id}/{start_unix}/{end_unix}/{tzi}/
    ?alarmed=true&limit=10000
```

### Call 3 — Alert Photo (per site, best-effort)
```
GET /api/map/external/{user_id}/{radar_id}/{server_track_id}/photos
```
- Download `presigned_photo_url` bytes immediately — URL expires in 1 hour.
- Graceful fallback: render report without photo if call fails or returns no results.

**Total live API calls per full monthly run: up to 18 calls (3 per site × 6 sites), executed sequentially with a short delay between sites to avoid rate-limiting.**

---

## 8. Data Pipeline (per site)

### `fetcher.py`

```python
# Pseudocode

async def fetch_site_monthly_data(site: RadarSite, year: int, month: int) -> dict:
    start_unix, end_unix = month_to_unix_range(year, month, tz=site.timezone)

    all_tracks = await m2_client.get_historical_tracks(
        radar_id=site.id,
        start=start_unix,
        end=end_unix,
        tzi=site.timezone,
        params={"limit": 10000}
    )

    alert_tracks = await m2_client.get_historical_tracks(
        radar_id=site.id,
        start=start_unix,
        end=end_unix,
        tzi=site.timezone,
        params={"limit": 10000, "alarmed": "true"}
    )

    alert_photo_bytes = await fetch_first_alert_photo(
        user_id=M2_USER_ID,
        radar_id=site.id,
        alert_tracks=alert_tracks["tracks"]
    )

    return {
        "site": site,
        "all_tracks": all_tracks["tracks"],
        "alert_tracks": alert_tracks["tracks"],
        "alert_photo": alert_photo_bytes,  # may be None
    }
```

### `aggregator.py`

Pure data transformation — no API calls. Unit-testable with fixture JSON.

```python
# Pseudocode

def aggregate(site: RadarSite, all_tracks: list, alert_tracks: list,
              year: int, month: int) -> dict:
    df = pd.DataFrame(all_tracks)
    df["started"] = pd.to_datetime(df["started"], utc=True)
    df["local_dt"] = df["started"].dt.tz_convert(site.timezone)

    total_count = len(df)
    alert_count = len(alert_tracks)

    alert_df = pd.DataFrame(alert_tracks)
    if not alert_df.empty:
        alert_df["local_dt"] = pd.to_datetime(
            alert_df["started"], utc=True
        ).dt.tz_convert(site.timezone)
        peak_hour = alert_df["local_dt"].dt.hour.value_counts().idxmax()
        busiest_weekday = alert_df["local_dt"].dt.weekday.value_counts().idxmax()
    else:
        peak_hour = None
        busiest_weekday = None

    df["date"] = df["local_dt"].dt.date
    daily_total = df.groupby("date").size().to_dict()

    alert_daily = {}
    if not alert_df.empty:
        alert_df["date"] = alert_df["local_dt"].dt.date
        alert_daily = alert_df.groupby("date").size().to_dict()

    # YoY from DB — may be None on first run
    baseline = db.get_baseline(site_id=site.id, year=year - 1, month=month)
    yoy_total_pct = compute_yoy(total_count, baseline.total_tracks) if baseline else None
    yoy_alert_pct = compute_yoy(alert_count, baseline.alert_tracks) if baseline else None

    return {
        "site": site,
        "year": year,
        "month": month,
        "total_tracks": total_count,
        "alert_tracks": alert_count,
        "peak_alert_hour": peak_hour,
        "busiest_weekday": WEEKDAY_ES[busiest_weekday] if busiest_weekday is not None else None,
        "daily_total": daily_total,
        "daily_alerts": alert_daily,
        "yoy_total_pct": yoy_total_pct,
        "yoy_alert_pct": yoy_alert_pct,
    }

# Spanish weekday lookup — avoids locale dependency in Docker
WEEKDAY_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}
```

### `chart_builder.py`

Produces the daily time-series chart as PNG bytes. Called once per site per run.

```python
# Pseudocode

def build_daily_chart(daily_total: dict, daily_alerts: dict,
                      year: int, month: int) -> bytes:
    # Two series: total registros (teal) + alertas (orange-red)
    # X-axis: all calendar days in the month
    # Y-axis: track count
    # Navy/teal palette matching Pronatura branding
    # Returns PNG bytes via io.BytesIO
```

---

## 9. Report Generation (`app/report/`)

### Flow (per site)
```
aggregated KPIs + chart PNG bytes + alert photo bytes + site metadata
        ↓
  Jinja2 renders monthly_report.html
  (site.name injected into title: "REPORTE DE ACTIVIDAD DEL M2 EN {site.name.upper()}")
        ↓
  WeasyPrint converts HTML → PDF
        ↓
  PDF saved to /app/reports/{site.slug}/YYYY_MM_{site.slug}.pdf
        ↓
  Path stored in ReportRun DB record
```

### Template notes
- Site name is injected dynamically — template is shared across all sites.
- Static assets (radar tower photo, Pronatura logo) live in `app/report/static/` and are site-agnostic.
- Alert photo is site-specific — passed as base64 bytes or omitted if unavailable.
- YoY labels ("Aumento" / "Disminución") only render when `yoy_pct` is not None.

### WeasyPrint Dockerfile deps
```dockerfile
RUN apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

---

## 10. Scheduler (`app/scheduler/jobs.py`)

One cron job. Iterates all active sites sequentially on the configured day of month.

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

scheduler.add_job(
    func=run_all_sites_job,
    trigger=CronTrigger(day=int(REPORT_RUN_DAY), hour=6, minute=0),
    id="monthly_report_all_sites",
    replace_existing=True,
)

scheduler.start()


def run_all_sites_job():
    """Runs on the configured day of month. Iterates all active sites."""
    year, month = get_previous_month()   # Reports on the month that just ended
    active_sites = db.get_active_sites()

    for site in active_sites:
        try:
            run_single_site(site, year, month, triggered_by="scheduler")
        except Exception as e:
            log.error(f"[{site.name}] Failed: {e}")
            db.update_report_run_status(site.id, year, month, "failed", str(e))
        finally:
            time.sleep(3)  # Brief pause between sites — avoids hammering the API


def run_single_site(site: RadarSite, year: int, month: int, triggered_by: str):
    """Pipeline for one site. Called by scheduler and by admin manual trigger."""
    run = db.create_report_run(site.id, year, month, triggered_by)

    data = fetcher.fetch_site_monthly_data(site, year, month)
    kpis = aggregator.aggregate(site, data["all_tracks"], data["alert_tracks"], year, month)
    chart_png = chart_builder.build_daily_chart(kpis["daily_total"], kpis["daily_alerts"], year, month)
    pdf_path = report.generator.generate_pdf(kpis, chart_png, data["alert_photo"])

    db.update_report_run_success(run.id, kpis, pdf_path)
    db.save_yoy_baseline(site.id, year, month, kpis["total_tracks"], kpis["alert_tracks"])

    recipients = db.get_active_recipients(site.id)
    if recipients:
        mailer.send_report(site, run, pdf_path, recipients)
    else:
        log.warning(f"[{site.name}] No active recipients — PDF generated but not sent.")
```

---

## 11. Mailer (`app/mailer/smtp_sender.py`)

```python
# Pseudocode

def send_report(site: RadarSite, run: ReportRun,
                pdf_path: str, recipients: list[Recipient]):

    subject = f"Reporte de Actividad M2 — {site.name} — {month_name(run.month)} {run.year}"
    body_html = render_email_body(site, run)
    to_addresses = [r.email for r in recipients]  # plain strings — NOT Recipient objects

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"{EMAIL_FROM_NAME} <{SMTP_USER}>"
    msg["To"] = ", ".join(to_addresses)

    msg.attach(MIMEText(body_html, "html"))

    filename = f"Reporte_M2_{site.slug}_{run.year}_{run.month:02d}.pdf"
    with open(pdf_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)

    with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:  # int() cast is mandatory
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_addresses, msg.as_string())
```

---

## 12. Admin Panel (`app/admin/`)

Flask + HTMX. Server-rendered partials. Single admin account via HTTP Basic Auth.

### Routes

| Route | Method | Description |
|---|---|---|
| `/admin/` | GET | Dashboard: card per site showing last run status, last run date, recipient count |
| `/admin/sites/<site_id>` | GET | Site detail: recipient list, report history, manual trigger button |
| `/admin/sites/<site_id>/recipients/add` | POST | Add recipient to this site |
| `/admin/sites/<site_id>/recipients/<id>/toggle` | POST | Toggle active/inactive (HTMX swap) |
| `/admin/sites/<site_id>/recipients/<id>/delete` | DELETE | Remove recipient from this site |
| `/admin/sites/<site_id>/run` | POST | Manually trigger report for this site (year/month selectable) |
| `/admin/sites/<site_id>/toggle` | POST | Enable/disable site from scheduled runs |
| `/admin/run/all` | POST | Manually trigger all active sites for a given year/month |
| `/admin/run/status` | GET | HTMX-polled endpoint: returns current run progress across all sites |
| `/admin/history` | GET | Global report history table, filterable by site |
| `/admin/history/<run_id>/download` | GET | Serve the PDF for download |
| `/admin/settings` | GET/POST | SMTP config test; YoY baseline editor (per site, per month) |

### Dashboard layout
- One card per site (6 cards).
- Each card shows: site name, last run date, last run status (green/red badge), recipient count, "Run Now" button.
- "Run All Sites" button at top triggers all active sites for a selected month.
- HTMX polls `/admin/run/status` every 3 seconds while a run is in progress, updating each site card status in place.

### Design
- Palette: navy (`#003366`) primary, teal (`#007E7A`) accent, white background — matches Pronatura report branding.
- Font: system sans-serif stack.
- Fixed sidebar with site list for quick navigation to site detail pages.
- No external CDN dependencies except HTMX (pinned version, self-hosted in `static/`).

---

## 13. Docker Setup

### `Dockerfile`
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "-m", "app"]
```

### `docker-compose.yml`
```yaml
version: "3.9"
services:
  m2-report:
    build: .
    restart: unless-stopped
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./reports:/app/reports
      - ./logs:/app/logs
      - ./data:/app/data       # SQLite DB lives here
```

---

## 14. `requirements.txt`

```
httpx==0.27.*
pandas==2.2.*
matplotlib==3.9.*
WeasyPrint==62.*
Jinja2==3.1.*
Flask==3.1.*
SQLAlchemy==2.0.*
APScheduler==3.10.*
python-dotenv==1.0.*
```

---

## 15. Full Data Pipeline (End-to-End)

```
[APScheduler cron — REPORT_RUN_DAY of month, 06:00]
        |
        ▼
[scheduler/jobs.py — run_all_sites_job()]
  └── get_active_sites() → [Loreto, Loreto2, SanBasilio, IslasMarias, ElPardito, EspirituSanto]
        |
        ▼ (for each site, sequentially)
[pipeline/fetcher.py — fetch_site_monthly_data(site, year, month)]
  ├── GET /historical/{site.id}/... (all tracks)
  ├── GET /historical/{site.id}/... (alarmed=true)
  └── GET /external/.../photos      (best-effort alert photo)
        |
        ▼
[pipeline/aggregator.py — aggregate(site, ...)]
  ├── total_tracks, alert_tracks
  ├── peak_alert_hour, busiest_weekday (Spanish, from lookup dict)
  ├── daily_total[], daily_alerts[]
  └── yoy_total_pct, yoy_alert_pct (from SQLite YoYBaseline, may be None)
        |
        ▼
[pipeline/chart_builder.py]
  └── matplotlib → PNG bytes
        |
        ▼
[report/generator.py]
  ├── Jinja2 renders monthly_report.html (site.name injected)
  └── WeasyPrint → PDF → /app/reports/{site.slug}/YYYY_MM_{site.slug}.pdf
        |
        ▼
[db/crud.py]
  ├── ReportRun updated (status=success, pdf_path, KPIs)
  └── YoYBaseline upserted for (site.id, year, month)
        |
        ▼
[mailer/smtp_sender.py]
  └── PDF sent to site's active Recipient list
        |
        ▼
[next site...]
```

---

## 16. Implementation Order for Claude Code

Build and test in this sequence — each step is independently testable before moving on:

1. **`app/db/`** — SQLAlchemy models (`RadarSite`, `Recipient`, `ReportRun`, `YoYBaseline`) + CRUD + `seed.py` to populate `RadarSite` rows on first boot.
2. **`app/config.py`** — load and validate all env vars; fail fast with a clear error message if any are missing; cast `SMTP_PORT` to `int()` explicitly here.
3. **`app/api/m2_client.py`** — `httpx` client with auth header, 3-attempt exponential backoff retry, typed response parsing.
4. **`app/pipeline/fetcher.py`** — orchestrate the 2–3 API calls per site; test against real token with a single site first.
5. **`app/pipeline/aggregator.py`** — pure data transformation; write unit tests with fixture JSON before wiring to live data.
6. **`app/pipeline/chart_builder.py`** — matplotlib chart; save PNG to disk and inspect visually before embedding in PDF.
7. **`app/report/`** — Jinja2 template + WeasyPrint; generate a sample PDF for San Basilio (id=45) and inspect layout.
8. **`app/mailer/smtp_sender.py`** — send to a single test address first; verify PDF attachment opens correctly.
9. **`app/scheduler/jobs.py`** — wire `run_single_site()` together; test by calling it directly before enabling the cron.
10. **`app/admin/`** — Flask Blueprint + all routes + HTMX partials; test manual trigger for one site end-to-end.
11. **`Dockerfile` + `docker-compose.yml`** — containerize; cold-start test with `docker compose up --build`.

---

## 17. Known Issues & Constraints

- **`SMTP_PORT` must be `int`:** `python-dotenv` reads all values as strings. Cast explicitly in `config.py` — this was the source of the prior mailer bug.
- **YoY baseline on first run:** `YoYBaseline` will be empty on first deployment. The template and aggregator must handle `yoy_pct = None` gracefully — omit the YoY label rather than crashing or rendering "None%".
- **Empty site:** If a site has zero tracks in a month (e.g. radar downtime), the aggregator must handle empty DataFrames without crashing. Generate the report with zeroes and a note.
- **API pagination:** Default `limit=10000` is sufficient for current volumes. If any site ever exceeds 10,000 tracks in a month, the fetcher must paginate (note: `page > 1` uses a fixed page size of 15 rows per API docs — very slow at scale). Add a warning log if any site's track count approaches 8,000.
- **`presigned_photo_url` expiry:** Expires after 1 hour. Download bytes immediately in `fetcher.py` — never store the URL for later retrieval.
- **Spanish weekday names:** Use the hardcoded `WEEKDAY_ES` dict in `aggregator.py` rather than `dt.day_name(locale="es_MX")` — the locale may not be installed in the Docker image and this avoids a silent failure.
- **Sequential site runs:** Sites run sequentially with a 3-second pause between them to avoid hammering the API. Total scheduled run time for 6 sites is well under 5 minutes at current track volumes.
- **Recipient list empty:** If a site has no active recipients, generate and save the PDF but skip the email send and log a warning. Do not treat this as a failure.
- **WeasyPrint startup check:** On first boot, generate a minimal 1-page test PDF to confirm WeasyPrint and its system dependencies are correctly installed. Fail fast with a clear error if this check fails.
- **`run_single_site()` is the shared entrypoint** for both the scheduler and the admin manual trigger. It must be safe to call from either context (background thread vs. HTTP request handler). Wrap in a try/except at both call sites.
