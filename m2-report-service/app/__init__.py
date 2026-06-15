"""Application factory for the M2 report service."""

import logging

from flask import Flask, redirect, url_for

from app.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def create_app() -> Flask:
    configure_logging()

    from app.db import init_db

    init_db()

    app = Flask(__name__)
    app.secret_key = settings.admin_secret_key

    from app.admin.routes import admin_bp

    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        from app.db import crud
        from app.pipeline.aggregator import MONTH_ES

        return {"nav_sites": crud.get_all_sites(), "month_es": MONTH_ES}

    @app.route("/")
    def index():
        return redirect(url_for("admin.dashboard"))

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
