"""Mint and revoke API keys. Prints plaintext once; stores SHA-256 only."""

from __future__ import annotations

import argparse
import secrets
import sys
from datetime import datetime, timezone

from sqlalchemy import select

from app.auth import hash_key
from app.db import SessionLocal, init_db
from app.models import ApiKey


def create_key(name: str) -> str:
    init_db()
    plaintext = "mf_live_" + secrets.token_urlsafe(32)
    digest = hash_key(plaintext)
    with SessionLocal() as db:
        if db.scalar(select(ApiKey).where(ApiKey.name == name)):
            raise SystemExit(f"key name already exists: {name}")
        db.add(
            ApiKey(
                name=name,
                key_hash=digest,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
        )
        db.commit()
    return plaintext


def revoke_key(name: str) -> None:
    init_db()
    with SessionLocal() as db:
        key = db.scalar(select(ApiKey).where(ApiKey.name == name))
        if key is None:
            raise SystemExit(f"unknown key name: {name}")
        key.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()


def list_keys() -> list[ApiKey]:
    init_db()
    with SessionLocal() as db:
        return list(db.scalars(select(ApiKey).order_by(ApiKey.id)).all())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage MovieFone API keys")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create = sub.add_parser("create", help="mint a key and print it once")
    create.add_argument("--name", required=True)

    revoke = sub.add_parser("revoke", help="revoke a key by name")
    revoke.add_argument("--name", required=True)

    sub.add_parser("list", help="list key names (never hashes' plaintext)")

    args = parser.parse_args(argv)
    if args.cmd == "create":
        token = create_key(args.name)
        print(token)
        print("store this now; it will not be shown again", file=sys.stderr)
        return 0
    if args.cmd == "revoke":
        revoke_key(args.name)
        print(f"revoked {args.name}")
        return 0
    for key in list_keys():
        state = "revoked" if key.revoked_at else "active"
        print(f"{key.name}\t{state}\t{key.created_at.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
