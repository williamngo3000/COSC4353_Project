def test_register_internal_error(monkeypatch, client):
    # Force db.session.commit to throw an exception
    def broken_commit():
        raise Exception("DB failure")

    monkeypatch.setattr("app.db.session.commit", lambda: broken_commit())

    resp = client.post("/register", json={"email": "fail@test.com", "password": "Password1"})
    assert resp.status_code == 500


def test_notification_mark_read_not_found(client):
    resp = client.put("/notifications/999999/read")
    assert resp.status_code == 404


def test_activity_endpoint(client):
    resp = client.get("/activity")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_delete_user_not_found(client):
    resp = client.delete("/users/notreal@example.com")
    assert resp.status_code == 404

