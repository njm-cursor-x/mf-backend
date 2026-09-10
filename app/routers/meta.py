from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db, latest_ingest
from app.models import Movie, Showtime, Theater
from app.schemas import MetaResponse
from app.config import settings

router = APIRouter(tags=["meta"], dependencies=[Depends(require_api_key)])


@router.get(
    "/meta",
    operation_id="get_meta",
    summary="Catalog freshness",
    description="How stale the listings are. Voice agents should mention this if ingest_status is not ok.",
    response_model=MetaResponse,
)
def get_meta(db: Session = Depends(get_db)) -> MetaResponse:
    run = latest_ingest(db)
    return MetaResponse(
        app=settings.mf_app_name,
        timezone=settings.mf_tz,
        as_of=run.finished_at if run else None,
        ingest_status=run.status if run else None,
        theater_count=db.scalar(select(func.count()).select_from(Theater)) or 0,
        movie_count=db.scalar(select(func.count()).select_from(Movie)) or 0,
        showtime_count=db.scalar(select(func.count()).select_from(Showtime)) or 0,
    )
