import hashlib
from collections.abc import Generator
from datetime import datetime, timezone

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.errors import ApiError
from app.models import ApiKey

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Key minted with `python -m app.keys create`. Example: mf_live_…",
)


def hash_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def upsert_boot_key(db: Session) -> None:
    plaintext = settings.mf_api_key.strip()
    if not plaintext:
        return
    digest = hash_key(plaintext)
    existing = db.scalar(select(ApiKey).where(ApiKey.name == "boot-env"))
    if existing:
        existing.key_hash = digest
        existing.revoked_at = None
    else:
        db.add(
            ApiKey(
                name="boot-env",
                key_hash=digest,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
        )
    db.commit()


def require_api_key(
    raw_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> ApiKey:
    if not raw_key:
        raise ApiError(401, "UNAUTHORIZED", "Missing or invalid API key.")
    digest = hash_key(raw_key)
    key = db.scalar(
        select(ApiKey).where(ApiKey.key_hash == digest, ApiKey.revoked_at.is_(None))
    )
    if key is None:
        raise ApiError(401, "UNAUTHORIZED", "Missing or invalid API key.")
    return key


AuthDep = Generator
