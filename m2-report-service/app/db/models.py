"""SQLAlchemy models for the M2 report service."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class RadarSite(Base):
    """One row per radar site. Seeded on first boot; id matches the M2 API radar_id."""

    __tablename__ = "radar_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    recipients: Mapped[list["Recipient"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )
    report_runs: Mapped[list["ReportRun"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )
    baselines: Mapped[list["YoYBaseline"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class Recipient(Base):
    """Per-site mailing list entry."""

    __tablename__ = "recipients"
    __table_args__ = (UniqueConstraint("site_id", "email", name="uq_recipient_site_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("radar_sites.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    site: Mapped[RadarSite] = relationship(back_populates="recipients")


class ReportRun(Base):
    """One row per site per month. A re-run overwrites the existing record."""

    __tablename__ = "report_runs"
    __table_args__ = (UniqueConstraint("site_id", "year", "month", name="uq_run_site_year_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("radar_sites.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    total_tracks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alert_tracks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peak_alert_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    busiest_weekday: Mapped[str | None] = mapped_column(String(16), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(16), nullable=False, default="scheduler")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped[RadarSite] = relationship(back_populates="report_runs")


class YoYBaseline(Base):
    """Prior-year KPIs per site per month. Upserted automatically on each successful run."""

    __tablename__ = "yoy_baselines"
    __table_args__ = (UniqueConstraint("site_id", "year", "month", name="uq_baseline_site_year_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("radar_sites.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tracks: Mapped[int] = mapped_column(Integer, nullable=False)
    alert_tracks: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    site: Mapped[RadarSite] = relationship(back_populates="baselines")


class AppSetting(Base):
    """Key-value store for runtime-editable settings (e.g. the global send schedule).

    Key-value avoids schema changes for new settings, since tables are created with
    create_all (no migrations). Values are strings; callers parse as needed.
    """

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
