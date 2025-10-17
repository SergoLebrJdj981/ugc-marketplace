"""Centralised Loguru configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from loguru import logger

from app.core.config import PROJECT_ROOT

LOG_DIR: Final[Path] = PROJECT_ROOT.parent / "logs"
APP_LOG = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "errors.log"

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        APP_LOG,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.add(
        ERROR_LOG,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    _configured = True
