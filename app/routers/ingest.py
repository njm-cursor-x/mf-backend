from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.errors import ApiError
from app.routers.meta import catalog_meta
from app.schemas import MetaResponse
from ingest.load import apply_snapshot
from ingest.schema import Snapshot

router = APIRouter(tags=["ingest"], dependencies=[Depends(require_api_key)])


@router.post(
    "/ingest/snapshots",
    operation_id="ingest_snapshot",
    summary="Load a showtimes snapshot into the live database",
    description=(
        "Cloud-agent refresh path. Replaces showtimes for theaters in the payload. "
        "Does not invent rows. Unknown theater or movie IDs are rejected. "
        "Voice agents can query immediately after this returns 200."
    ),
    response_model=MetaResponse,
)
def ingest_snapshot(snapshot: Snapshot, db: Session = Depends(get_db)) -> MetaResponse:
    try:
        apply_snapshot(db, snapshot, "http:ingest", snapshot.source)
    except ValueError as exc:
        raise ApiError(400, "INGEST_INVALID", str(exc)) from exc
    return catalog_meta(db)
