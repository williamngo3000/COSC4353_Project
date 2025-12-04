import pytest
from app import app
from models import db, UserCredentials, EventDetails

# Helper: simulate failing DB commit
def failing_commit():
    raise Exception("Forced DB failure")


def test_register_internal_error(monkeypatch, client):
    # Force db.session.commit() to throw
    monkeypatch.setattr("app.db.session.commit", failing_commit)

    r = client.post("/register", json={"email": "x@test.com", "password": "Password1"})
    assert r.status_code == 500


def test_login_internal_error(monkeypatch, client):
    """
    Fix: Replace the entire SQLAlchemy query object so that login hits
    the exception block instead of returning 401.
    """
    class BrokenQuery:
        def filter_by(self, **kwargs):
            raise Exception("DB FAILURE")

    # Patch UserCredentials.query entirely
    monkeypatch.setattr("app.UserCredentials.query", BrokenQuery())

    r = client.post("/login", json={"email": "admin@example.com", "password": "Password1"})
    assert r.status_code == 500


def test_events_post_internal_error(monkeypatch, client):
    monkeypatch.setattr("app.db.session.commit", failing_commit)

    r = client.post("/events", json={"event_name": "X"})
    assert r.status_code == 500


def test_invites_get_internal_error(monkeypatch, client):
    # Must patch query attribute, not call
    class BrokenInviteQuery:
        def filter_by(self, **kwargs):
            raise Exception("DB FAILURE")

        def order_by(self, *args, **kwargs):
            raise Exception("DB FAILURE")

    monkeypatch.setattr("app.EventInvite.query", BrokenInviteQuery())

    r = client.get("/invites")
    assert r.status_code == 500


def test_users_get_internal_error(monkeypatch, client):
    # Patch entire query so .all() fails
    class BrokenUserQuery:
        def all(self):
            raise Exception("DB FAILURE")

    monkeypatch.setattr("app.UserCredentials.query", BrokenUserQuery())

    r = client.get("/users")
    assert r.status_code == 500


def test_notifications_internal_error(monkeypatch, client):
    # Patch query so filter_by() → exception
    class BrokenNotifQuery:
        def filter_by(self, **kwargs):
            raise Exception("DB FAILURE")

    monkeypatch.setattr("app.Notification.query", BrokenNotifQuery())

    r = client.get("/notifications")
    assert r.status_code == 500

