from fastapi import APIRouter, Depends, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.errors import ApiError
from app.models import Theater, ZipCode, ZipTheater
from app.schemas import TheaterSummary, ZipResolved

router = APIRouter(tags=["zips"], dependencies=[Depends(require_api_key)])


def _theater_summary(theater: Theater) -> TheaterSummary:
    return TheaterSummary(
        id=theater.id,
        name=theater.name,
        chain=theater.chain,
        address=theater.address,
        zip_code=theater.zip_code,
        neighborhood=theater.neighborhood,
    )


@router.get(
    "/zips/{zip_code}",
    operation_id="resolve_zip",
    summary="Resolve a Manhattan ZIP to nearby theaters",
    description="Spoken ZIP from the caller. Non-Manhattan ZIPs return OUT_OF_AREA.",
    response_model=ZipResolved,
    responses={
        404: {
            "description": "ZIP is not in the Manhattan roster",
            "content": {
                "application/json": {
                    "example": {
                        "code": "OUT_OF_AREA",
                        "message": "No listings for that ZIP. Coverage is Manhattan only.",
                        "details": {"zip_code": "11201"},
                    }
                }
            },
        }
    },
)
def resolve_zip(
    zip_code: str = Path(..., min_length=5, max_length=5, examples=["10023"]),
    db: Session = Depends(get_db),
) -> ZipResolved:
    zip_row = db.get(ZipCode, zip_code)
    if zip_row is None:
        raise ApiError(
            404,
            "OUT_OF_AREA",
            "No listings for that ZIP. Coverage is Manhattan only.",
            {"zip_code": zip_code},
        )
    theater_ids = list(
        db.scalars(select(ZipTheater.theater_id).where(ZipTheater.zip_code == zip_code))
    )
    theaters = list(db.scalars(select(Theater).where(Theater.id.in_(theater_ids))))
    theaters.sort(key=lambda t: t.name)
    return ZipResolved(
        zip_code=zip_row.zip_code,
        neighborhood=zip_row.neighborhood,
        borough=zip_row.borough,
        theaters=[_theater_summary(t) for t in theaters],
    )
