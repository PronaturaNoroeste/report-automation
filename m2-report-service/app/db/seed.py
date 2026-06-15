"""Seed the RadarSite registry on first boot.

These are the only radar IDs the API token has access to. Idempotent:
existing rows are never overwritten (the admin panel owns `active` after boot).

Timezone note: all six sites are in Baja California Sur / Islas Marías
(Nayarit offshore). BCS uses America/Mazatlan (UTC-7, no DST since 2022).
Confirm with Pronatura if a site should differ.
"""

import logging

from app.db.models import RadarSite

log = logging.getLogger(__name__)

RADAR_SITES = [
    {"id": 23, "name": "Loreto",         "slug": "loreto",          "timezone": "America/Mazatlan"},
    {"id": 42, "name": "Loreto 2",       "slug": "loreto_2",        "timezone": "America/Mazatlan"},
    {"id": 45, "name": "San Basilio",    "slug": "san_basilio",     "timezone": "America/Mazatlan"},
    {"id": 48, "name": "Islas Marías",   "slug": "islas_marias",    "timezone": "America/Mazatlan"},
    {"id": 55, "name": "El Pardito",     "slug": "el_pardito",      "timezone": "America/Mazatlan"},
    {"id": 60, "name": "Espíritu Santo", "slug": "espiritu_santo",  "timezone": "America/Mazatlan"},
]


def seed_radar_sites() -> None:
    from app.db import SessionLocal

    with SessionLocal() as session:
        existing_ids = {row.id for row in session.query(RadarSite.id).all()}
        new_sites = [RadarSite(**data) for data in RADAR_SITES if data["id"] not in existing_ids]
        if new_sites:
            session.add_all(new_sites)
            session.commit()
            log.info("Seeded %d radar sites: %s", len(new_sites), [s.name for s in new_sites])
