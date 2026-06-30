"""Service entrypoint: `python -m app`.

Boots in order: config (validated at import), DB + seed, WeasyPrint startup
check, scheduler, then the Flask admin panel in the foreground.
"""

import logging

from app import create_app
from app.report import generator
from app.scheduler import jobs

log = logging.getLogger(__name__)


def main() -> None:
    app = create_app()

    # Fail fast if WeasyPrint's system deps (pango/cairo) are broken.
    generator.startup_check()
    log.info("WeasyPrint startup check passed.")

    jobs.start_scheduler()

    # Single-process service: waitress serves the admin panel while APScheduler
    # runs in a background thread. Must stay one process (in-process scheduler +
    # SQLite), so a single multi-threaded server — not multi-worker gunicorn.
    #
    # Binds all interfaces *inside the container*; public exposure is controlled
    # outside the app: docker-compose publishes the port to host loopback only
    # (127.0.0.1) and a Cloudflare Tunnel sidecar provides TLS to the internet.
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000, threads=8)


if __name__ == "__main__":
    main()
