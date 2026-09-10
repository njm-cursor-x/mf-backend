from sqlalchemy import select

from app.auth import hash_key
from app.db import SessionLocal
from app.keys import create_key, revoke_key
from app.models import ApiKey


def test_create_and_revoke_key(client, auth_headers):
    token = create_key("grok-voice")
    assert token.startswith("mf_live_")
    with SessionLocal() as db:
        row = db.scalar(select(ApiKey).where(ApiKey.name == "grok-voice"))
        assert row is not None
        assert row.key_hash == hash_key(token)
        assert row.revoked_at is None

    ok = client.get("/meta", headers={"X-API-Key": token})
    assert ok.status_code == 200

    revoke_key("grok-voice")
    dead = client.get("/meta", headers={"X-API-Key": token})
    assert dead.status_code == 401
