import hashlib
import os
from collections.abc import Generator
from datetime import datetime, timezone

from fastapi import Depends, Request, Security
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


def _clean_secret(value: str | None) -> str:
    return (value or "").strip().strip('"').strip("'")


def boot_key_plaintext() -> str:
    return _clean_secret(os.environ.get("MF_API_KEY") or settings.mf_api_key)


def extract_presented_key(request: Request, header_key: str | None) -> str:
    presented = _clean_secret(header_key) or _clean_secret(request.headers.get("x-api-key"))
    if presented:
        return presented
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return _clean_secret(auth[7:])
    return ""


def upsert_boot_key(db: Session) -> None:
    plaintext = boot_key_plaintext()
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
    request: Request,
    raw_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> ApiKey:
    presented = extract_presented_key(request, raw_key)
    if not presented:
        raise ApiError(401, "UNAUTHORIZED", "Missing or invalid API key.")
    digest = hash_key(presented)
    boot = boot_key_plaintext()
    if boot and hash_key(boot) == digest:
        return ApiKey(
            name="boot-env",
            key_hash=digest,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
    key = db.scalar(
        select(ApiKey).where(ApiKey.key_hash == digest, ApiKey.revoked_at.is_(None))
    )
    if key is None:
        raise ApiError(401, "UNAUTHORIZED", "Missing or invalid API key.")
    return key


AuthDep = Generator
