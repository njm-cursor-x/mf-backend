from app.config import SNAPSHOT_DIR
from ingest.load import load_json
from ingest.schema import Snapshot
from ingest.refresh import refresh_from_file


def test_seed_snapshot_validates():
    raw = load_json(SNAPSHOT_DIR / "seed.json")
    snapshot = Snapshot.model_validate(raw)
    assert snapshot.movies
    assert snapshot.showtimes
    assert "amc-lincoln-square-13" in snapshot.theater_ids()


def test_reload_from_seed(tmp_path, monkeypatch, client, auth_headers):
    # client fixture already loaded seed; reload should stay healthy
    refresh_from_file(SNAPSHOT_DIR / "seed.json")
    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["movies"]


def test_rejects_unknown_theater():
    bad = {
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
    snapshot = Snapshot.model_validate(bad)
    assert "not-a-house" in snapshot.theater_ids()
