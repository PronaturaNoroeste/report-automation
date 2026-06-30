"""Global send-schedule config: crud accessors + the settings route."""

import base64

import pytest
from sqlalchemy import delete

from app.db import SessionLocal, crud
from app.db.models import AppSetting


def _clear_settings():
    with SessionLocal() as s:
        s.execute(delete(AppSetting))
        s.commit()


def test_get_schedule_defaults():
    _clear_settings()
    day, hour, minute = crud.get_schedule()
    assert (hour, minute) == (6, 0)      # default time
    assert 1 <= day <= 28                # env default day


def test_set_and_get_schedule_roundtrip():
    crud.set_schedule(15, 8, 30)
    assert crud.get_schedule() == (15, 8, 30)
    crud.set_schedule(3, 22, 5)          # upsert
    assert crud.get_schedule() == (3, 22, 5)


# --------------------------------------------------------------- route

@pytest.fixture
def client():
    from app import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _auth():
    return {"Authorization": "Basic " + base64.b64encode(b"admin:admin-pass").decode()}


def _same_origin():
    return {**_auth(), "Origin": "http://localhost"}


def test_settings_get_renders(client):
    resp = client.get("/admin/settings", headers=_auth())
    assert resp.status_code == 200
    assert "Programación".encode() in resp.data


def test_settings_post_valid_updates_schedule(client):
    resp = client.post("/admin/settings",
                       data={"day": "10", "time": "07:15"},
                       headers=_same_origin())
    assert resp.status_code in (302, 303)        # redirect after POST
    assert crud.get_schedule() == (10, 7, 15)


def test_settings_post_out_of_range_is_rejected(client):
    crud.set_schedule(5, 5, 5)
    resp = client.post("/admin/settings",
                       data={"day": "31", "time": "07:15"},  # day > 28
                       headers=_same_origin())
    assert resp.status_code in (302, 303)
    assert crud.get_schedule() == (5, 5, 5)      # unchanged


def test_settings_post_is_csrf_protected(client):
    crud.set_schedule(5, 5, 5)
    resp = client.post("/admin/settings",
                       data={"day": "10", "time": "07:15"},
                       headers={**_auth(), "Origin": "https://evil.example"})
    assert resp.status_code == 403
    assert crud.get_schedule() == (5, 5, 5)      # unchanged
