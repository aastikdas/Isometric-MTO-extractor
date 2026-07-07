"""
Application configuration loaded from environment variables.

Uses python-dotenv so a local `.env` file is picked up during development.
"""

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def _parse_cors_origins(raw: str | None) -> List[str]:
    """Parse a comma-separated list of allowed CORS origins."""
    if not raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Settings(BaseModel):
    """Centralised settings for the FastAPI application."""

    # Application metadata
    app_name: str = "Isometric MTO Extractor API"
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS — comma-separated origins in .env, e.g. "http://localhost:3000"
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
    )

    # Gemini Vision — when empty, /extract falls back to mock data
    gemini_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (one per process)."""
    return Settings(
        app_name=os.getenv("APP_NAME", "Isometric MTO Extractor API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"},
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
    )
