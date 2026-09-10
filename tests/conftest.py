import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEST_KEY = "mf_live_test_key_for_unit_tests_only"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MF_API_KEY", TEST_KEY)
    from app import auth, config, db, main
    from ingest.load import bootstrap_if_empty

    db_path = tmp_path / "showtimes.db"
    monkeypatch.setattr(config.settings, "mf_api_key", TEST_KEY)
    monkeypatch.setattr(config.settings, "mf_db_path", db_path)
    db.configure_engine(db_path)
    db.init_db()
    with db.SessionLocal() as session:
        bootstrap_if_empty(session)
        auth.upsert_boot_key(session)
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    return {"X-API-Key": TEST_KEY}
