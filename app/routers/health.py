import os

from fastapi import APIRouter

from app.auth import boot_key_plaintext
from app.schemas import HealthResponse

router = APIRouter(tags=["meta"])


@router.get(
    "/health",
    operation_id="health",
    summary="Liveness check",
    description="Public. No API key. Use this for Railway/uptime probes.",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA") or os.environ.get("RAILWAY_GIT_COMMIT") or ""
    return HealthResponse(
        status="ok",
        api_key_configured=bool(boot_key_plaintext()),
        commit=sha[:8],
    )
