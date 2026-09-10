from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str = Field(examples=["UNAUTHORIZED"])
    message: str = Field(examples=["Missing or invalid API key."])
    details: dict = Field(default_factory=dict)


class ApiError(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorBody(
            code=exc.code,
            message=str(exc.detail),
            details=exc.details,
        ).model_dump(),
    )
