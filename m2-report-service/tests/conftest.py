"""Test environment: fake env vars + throwaway SQLite DB, set before any app import."""

import os
import tempfile

_tmpdir = tempfile.mkdtemp(prefix="m2_test_")

os.environ.update({
    "M2_API_BASE_URL": "https://example.test/api/map",
    "M2_API_TOKEN": "test-token",
    "SMTP_HOST": "smtp.example.test",
    "SMTP_PORT": "587",
    "SMTP_USER": "test@example.test",
    "SMTP_PASSWORD": "secret",
    "ADMIN_SECRET_KEY": "test-secret-key",
    "ADMIN_USERNAME": "admin",
    "ADMIN_PASSWORD": "admin-pass",
    "REPORT_OUTPUT_DIR": os.path.join(_tmpdir, "reports"),
    "DATA_DIR": _tmpdir,
    "DATABASE_URL": f"sqlite:///{os.path.join(_tmpdir, 'test.db')}",
    "LOG_LEVEL": "WARNING",
})

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def database():
    from app.db import init_db

    init_db()
    yield
