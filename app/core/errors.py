from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.error import ErrorEnvelope


def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    payload = ErrorEnvelope(
        error={
            "code": f"http_{exc.status_code}",
            "message": str(exc.detail),
            "details": None,
        }
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in exc.errors()]
    payload = ErrorEnvelope(
        error={
            "code": "validation_error",
            "message": "Request validation failed.",
            "details": details,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
    )


def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    payload = ErrorEnvelope(
        error={
            "code": "internal_server_error",
            "message": "An unexpected error occurred.",
            "details": None,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump(),
    )
