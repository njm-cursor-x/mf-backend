def test_health_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_key(client):
    response = client.get("/meta")
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHORIZED"
    assert "details" in body


def test_invalid_key(client):
    response = client.get("/meta", headers={"X-API-Key": "mf_live_nope"})
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_valid_key(client, auth_headers):
    response = client.get("/meta", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["movie_count"] >= 1
    assert body["theater_count"] == 12


def test_env_key_works_without_db_row(client, monkeypatch):
    monkeypatch.setenv("MF_API_KEY", "mf_live_only_in_env_not_in_db")
    response = client.get("/meta", headers={"X-API-Key": "mf_live_only_in_env_not_in_db"})
    assert response.status_code == 200
