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
    secret_key: str
    refresh_secret_key: str
    algorithm: str
    access_token_expires_minutes: int
    refresh_token_expires_days: int
    allowed_origins: list[str]
    rate_limit_per_minute: int
    log_path: Path

    def __init__(self) -> None:
        default_url = "postgresql+psycopg://postgres:postgres@localhost:5432/ugc_marketplace"
        self.database_url = os.getenv("DATABASE_URL", default_url)
        secret = os.getenv("SECRET_KEY", "change_me_secret")
        refresh_secret = os.getenv("REFRESH_SECRET_KEY", secret)
        self.secret_key = secret
        self.refresh_secret_key = refresh_secret
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expires_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
        self.refresh_token_expires_days = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))
        allowed = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        self.allowed_origins = [origin.strip() for origin in allowed.split(",") if origin.strip()]
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        log_path = os.getenv("LOG_PATH", str(PROJECT_ROOT / "logs" / "app.log"))
        self.log_path = Path(log_path)


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
