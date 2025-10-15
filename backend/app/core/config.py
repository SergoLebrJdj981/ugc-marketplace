"""Application settings and environment configuration."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Attempt to load environment variables from the project root .env if present
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Centralised runtime configuration."""

    app_name: str = "UGC Marketplace API"
    database_url: str

    def __init__(self) -> None:
        default_url = "postgresql+psycopg://postgres:postgres@localhost:5432/ugc_marketplace"
        self.database_url = os.getenv("DATABASE_URL", default_url)


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
