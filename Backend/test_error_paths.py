import pytest
from app import app
from models import db, UserCredentials, EventDetails

# Helper failing commit
def failing_commit():
    raise Exception("Forced DB failure")


def test_register_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.db.session.commit", failing_commit)
    r = client.post("/register", json={"email": "x@test.com", "password": "Password1"})
    assert r.status_code == 500


def test_login_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.UserCredentials.query.filter_by", lambda **kwargs: (_ for _ in ()).throw(Exception("ERR")))
    r = client.post("/login", json={"email": "admin@example.com", "password": "Password1"})
    assert r.status_code == 500


def test_events_post_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.db.session.commit", failing_commit)
    r = client.post("/events", json={"event_name": "X"})
    # Should hit internal error block
    assert r.status_code == 500


def test_invites_get_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.EventInvite.query", lambda: (_ for _ in ()).throw(Exception("ERR")))
    r = client.get("/invites")
    assert r.status_code == 500


def test_users_get_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.UserCredentials.query", lambda: (_ for _ in ()).throw(Exception("ERR")))
    r = client.get("/users")
    assert r.status_code == 500


def test_notifications_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.Notification.query", lambda: (_ for _ in ()).throw(Exception("ERR")))
    r = client.get("/notifications")
    assert r.status_code == 500

