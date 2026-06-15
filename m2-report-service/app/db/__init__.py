"""Database engine and session factory."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.models import Base

# SQLite needs check_same_thread=False because the scheduler thread and Flask
# request threads share the engine. Each unit of work gets its own session.
_connect_args = {}
if settings.database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False
    db_path = settings.database_url.replace("sqlite:///", "", 1)
    if db_path and db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Create tables and seed radar sites. Safe to call on every boot."""
    Base.metadata.create_all(engine)
    from app.db.seed import seed_radar_sites

    seed_radar_sites()
