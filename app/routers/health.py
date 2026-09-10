from fastapi import APIRouter

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
    return HealthResponse(status="ok")
