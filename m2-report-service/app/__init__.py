"""Application factory for the M2 report service."""

import logging
from urllib.parse import urlparse

from flask import Flask, abort, redirect, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import settings

log = logging.getLogger(__name__)

# Methods that cannot change state need no CSRF origin check.
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _allowed_origin_host() -> str:
    """Host that cross-origin checks compare against. Prefer the configured
    public origin (correct behind Cloudflare); fall back to the request host."""
    if settings.app_base_url:
        return urlparse(settings.app_base_url).netloc
    return request.host


def _reject_cross_origin() -> None:
    """CSRF guard: state-changing requests must originate from our own site.

    Browsers attach a trustworthy Origin (or Referer) header that page
    JavaScript cannot forge, so a same-origin check blocks cross-site form
    POSTs that would otherwise ride the cached Basic Auth credentials.
    """
    if request.method in _SAFE_METHODS:
        return
    allowed = _allowed_origin_host()
    origin = request.headers.get("Origin")
    if origin:
        source = urlparse(origin).netloc
    else:
        # No Origin (older browsers, some same-origin POSTs) → fall back to Referer.
        referer = request.headers.get("Referer")
        source = urlparse(referer).netloc if referer else ""
    if not source or source != allowed:
        log.warning("Blocked cross-origin %s %s (origin/referer host=%r, expected=%r)",
                    request.method, request.path, source, allowed)
        abort(403)


def create_app() -> Flask:
    configure_logging()

    from app.db import init_db

    init_db()

    app = Flask(__name__)
    app.secret_key = settings.admin_secret_key

    # Behind Cloudflare Tunnel / reverse proxy: trust one hop for scheme & host
    # so url_for(_external) and Secure cookies see https.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # The session cookie only backs flash messages, but harden it anyway.
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=bool(settings.app_base_url),
    )

    app.before_request(_reject_cross_origin)

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
