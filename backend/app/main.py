"""
FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import Settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown hooks."""
    # Startup: settings are loaded once and cached via get_settings().
    settings: Settings = get_settings()
    app.state.settings = settings
    yield
    # Shutdown: add cleanup here (DB pools, clients) when needed.


def create_app() -> FastAPI:
    """
    Application factory — builds and configures the FastAPI instance.

    Returns:
        A fully configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Allow the Next.js frontend to call this API during development.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all route handlers under the root prefix.
    app.include_router(router)

    return app


# Uvicorn import target: `uvicorn app.main:app`
app = create_app()
