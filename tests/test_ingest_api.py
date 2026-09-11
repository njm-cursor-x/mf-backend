from app.config import SNAPSHOT_DIR
from ingest.load import load_json


def test_ingest_requires_key(client):
    response = client.post("/ingest/snapshots", json={"source": "test", "movies": [], "showtimes": []})
    assert response.status_code == 401


def test_ingest_rejects_unknown_theater(client, auth_headers):
    payload = {
        "source": "test",
        "movies": [
            {
                "id": "x",
                "title": "X",
                "rating": "PG",
                "runtime_min": 90,
                "synopsis": "n/a",
            }
        ],
        "showtimes": [
            {
                "theater_id": "not-a-house",
                "movie_id": "x",
                "format": "standard",
                "times": ["12:00"],
                "days": [0],
            }
        ],
    }
    response = client.post("/ingest/snapshots", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["code"] == "INGEST_INVALID"


def test_ingest_loads_snapshot_for_queries(client, auth_headers):
    payload = {
        "source": "test-live",
        "movies": [
            {
                "id": "refresh-probe",
                "title": "Refresh Probe",
                "rating": "PG",
                "runtime_min": 90,
                "synopsis": "Used to prove live ingest.",
            }
        ],
        "showtimes": [
            {
                "theater_id": "amc-lincoln-square-13",
                "movie_id": "refresh-probe",
                "format": "standard",
                "times": ["16:40"],
                "days": [0],
            }
        ],
    }
    response = client.post("/ingest/snapshots", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["ingest_status"] == "ok"
    assert body["showtime_count"] >= 1

    movies = client.get("/movies/search?q=refresh%20probe", headers=auth_headers)
    assert movies.status_code == 200
    titles = [row["title"] for row in movies.json()["matches"]]
    assert "Refresh Probe" in titles

    meta = client.get("/meta", headers=auth_headers)
    assert meta.status_code == 200
    assert meta.json()["ingest_status"] == "ok"


def test_ingest_accepts_seed_snapshot(client, auth_headers):
    payload = load_json(SNAPSHOT_DIR / "seed.json")
    response = client.post("/ingest/snapshots", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["movie_count"] >= 1
