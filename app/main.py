from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes_health import router as health_router
from app.api.routes_ratings import router as ratings_router
from app.api.routes_spots import router as spots_router
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.settings import API_TITLE, API_VERSION, CORS_ALLOW_ORIGINS


def create_app() -> FastAPI:
    app = FastAPI(title=API_TITLE, version=API_VERSION)
    allow_all_origins = "*" in CORS_ALLOW_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all_origins else CORS_ALLOW_ORIGINS,
        allow_credentials=not allow_all_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(health_router)
    app.include_router(spots_router)
    app.include_router(ratings_router)
    app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
    return app


app = create_app()
