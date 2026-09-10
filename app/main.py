import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.auth import upsert_boot_key
from app.config import settings
from app.db import SessionLocal, init_db
from app.errors import ApiError, ErrorBody, api_error_handler
from app.routers import health, ingest, meta, movies, showtimes, theaters, zips
from ingest.load import bootstrap_if_empty

ERROR_RESPONSES = {
    400: {"model": ErrorBody, "description": "Bad request"},
    401: {"model": ErrorBody, "description": "Missing or invalid API key"},
    404: {"model": ErrorBody, "description": "Not found or out of area"},
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    with SessionLocal() as db:
        bootstrap_if_empty(db)
        upsert_boot_key(db)
    print(
        "startup: MF_API_KEY configured=" + str(bool(os.environ.get("MF_API_KEY"))),
        flush=True,
    )
    yield


app = FastAPI(
    title=settings.mf_app_name,
    summary="Manhattan movie showtimes for a voice agent. Unofficial MovieFone recreation.",
    description=(
        "Query ZIP, then a spoken movie title, then showtimes. "
        "All query routes require the `X-API-Key` header. "
        "`POST /ingest/snapshots` loads a validated snapshot into the live database. "
        "`GET /health` is public. Coverage is Manhattan only."
    ),
    version="0.1.0",
    lifespan=lifespan,
    responses=ERROR_RESPONSES,
)

app.add_exception_handler(ApiError, api_error_handler)
app.include_router(health.router)
app.include_router(meta.router)
app.include_router(ingest.router)
app.include_router(zips.router)
app.include_router(movies.router)
app.include_router(theaters.router)
app.include_router(showtimes.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
    )
    schema["components"] = schema.get("components", {})
    schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Mint with `python -m app.keys create --name grok-voice`.",
        }
    }
    schema["security"] = [{"ApiKeyAuth": []}]
    if "/health" in schema.get("paths", {}):
        schema["paths"]["/health"]["get"]["security"] = []
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
