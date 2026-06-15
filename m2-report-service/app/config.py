"""Application configuration.

Loads .env, validates required variables, and exposes typed settings.
Fails fast at import time with a clear error listing every missing variable.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_REQUIRED_VARS = [
    "M2_API_BASE_URL",
    "M2_API_TOKEN",
    "M2_USER_ID",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "ADMIN_SECRET_KEY",
    "ADMIN_USERNAME",
    "ADMIN_PASSWORD",
]


@dataclass(frozen=True)
class Settings:
    # ProtectedSeas M2 API
    m2_api_base_url: str
    m2_api_token: str
    m2_user_id: str

    # SMTP
    smtp_host: str
    smtp_port: int  # cast from str — python-dotenv reads everything as string
    smtp_user: str
    smtp_password: str
    email_from_name: str

    # Admin panel
    admin_secret_key: str
    admin_username: str
    admin_password: str

    # Service
    report_output_dir: Path
    log_level: str
    report_run_day: int
    database_url: str


def _load_settings() -> Settings:
    missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in the values."
        )

    smtp_port_raw = os.environ["SMTP_PORT"]
    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        raise RuntimeError(f"SMTP_PORT must be an integer, got: {smtp_port_raw!r}")

    report_run_day_raw = os.getenv("REPORT_RUN_DAY", "2")
    try:
        report_run_day = int(report_run_day_raw)
    except ValueError:
        raise RuntimeError(f"REPORT_RUN_DAY must be an integer, got: {report_run_day_raw!r}")
    if not 1 <= report_run_day <= 28:
        raise RuntimeError("REPORT_RUN_DAY must be between 1 and 28 (every month has these days)")

    report_output_dir = Path(os.getenv("REPORT_OUTPUT_DIR", "/app/reports"))

    data_dir = Path(os.getenv("DATA_DIR", "/app/data"))
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{data_dir / 'm2_reports.db'}")

    return Settings(
        m2_api_base_url=os.environ["M2_API_BASE_URL"].rstrip("/"),
        m2_api_token=os.environ["M2_API_TOKEN"],
        m2_user_id=os.environ["M2_USER_ID"],
        smtp_host=os.environ["SMTP_HOST"],
        smtp_port=smtp_port,
        smtp_user=os.environ["SMTP_USER"],
        smtp_password=os.environ["SMTP_PASSWORD"],
        email_from_name=os.getenv("EMAIL_FROM_NAME", "Monitor Marino Pronatura Noroeste"),
        admin_secret_key=os.environ["ADMIN_SECRET_KEY"],
        admin_username=os.environ["ADMIN_USERNAME"],
        admin_password=os.environ["ADMIN_PASSWORD"],
        report_output_dir=report_output_dir,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        report_run_day=report_run_day,
        database_url=database_url,
    )


settings = _load_settings()
