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

    # Single-process service: Flask serves the admin panel; APScheduler runs
    # in a background thread. debug/reloader stay off so the scheduler is not
    # started twice.
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
