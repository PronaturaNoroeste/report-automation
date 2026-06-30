"""CSRF origin-guard coverage (app/__init__.py _reject_cross_origin).

APP_BASE_URL is unset in the test env, so the guard falls back to the request
host, which the Flask test client sets to "localhost".
"""

import base64

import pytest


@pytest.fixture
def client():
    from app import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _auth():
    raw = base64.b64encode(b"admin:admin-pass").decode()
    return {"Authorization": f"Basic {raw}"}


ADD = "/admin/sites/23/recipients/add"  # site 23 is seeded
FORM = {"name": "Test", "email": "csrf@example.test"}


def test_post_without_origin_is_blocked(client):
    resp = client.post(ADD, data=FORM, headers=_auth())
    assert resp.status_code == 403


def test_post_with_foreign_origin_is_blocked(client):
    resp = client.post(ADD, data=FORM, headers={**_auth(), "Origin": "https://evil.example"})
    assert resp.status_code == 403


def test_post_with_foreign_referer_is_blocked(client):
    resp = client.post(ADD, data=FORM, headers={**_auth(), "Referer": "https://evil.example/x"})
    assert resp.status_code == 403


def test_guard_runs_before_auth(client):
    # Cross-origin is rejected (403) even without valid credentials — the guard
    # is a before_request hook, so it fires ahead of the @requires_auth view.
    resp = client.post(ADD, data=FORM, headers={"Origin": "https://evil.example"})
    assert resp.status_code == 403


def test_same_origin_post_passes_guard(client):
    resp = client.post(ADD, data=FORM, headers={**_auth(), "Origin": "http://localhost"})
    assert resp.status_code != 403  # 200 partial render — CSRF guard allowed it


def test_same_origin_via_referer_passes_guard(client):
    resp = client.post(ADD, data={"name": "Ref", "email": "ref@example.test"},
                       headers={**_auth(), "Referer": "http://localhost/admin/sites/23"})
    assert resp.status_code != 403


def test_safe_get_is_not_blocked(client):
    resp = client.get("/admin/", headers=_auth())
    assert resp.status_code == 200
