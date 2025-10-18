"""Centralised Loguru configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from loguru import logger

from app.core.config import PROJECT_ROOT

LOG_DIR: Final[Path] = PROJECT_ROOT.parent / "logs"
APP_LOG = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "errors.log"
CHAT_LOG = LOG_DIR / "chat.log"
NOTIFICATION_LOG = LOG_DIR / "notifications.log"
TELEGRAM_LOG = LOG_DIR / "telegram.log"
PAYMENTS_LOG = LOG_DIR / "payments.log"
BANK_WEBHOOK_LOG = LOG_DIR / "bank_webhooks.log"
FEES_LOG = LOG_DIR / "fees.log"

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()
    CHAT_LOG.touch(exist_ok=True)
    NOTIFICATION_LOG.touch(exist_ok=True)
    TELEGRAM_LOG.touch(exist_ok=True)
    PAYMENTS_LOG.touch(exist_ok=True)
    BANK_WEBHOOK_LOG.touch(exist_ok=True)
    FEES_LOG.touch(exist_ok=True)
    logger.add(
        APP_LOG,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        enqueue=False,
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
    logger.add(
        CHAT_LOG,
        level="INFO",
        rotation="5 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "chat",
        format="{message}",
    )
    logger.add(
        NOTIFICATION_LOG,
        level="INFO",
        rotation="5 MB",
        retention="14 days",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "notifications",
        format="{message}",
    )
    logger.add(
        TELEGRAM_LOG,
        level="INFO",
        rotation="5 MB",
        retention="14 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "telegram",
        format="{message}",
    )
    logger.add(
        PAYMENTS_LOG,
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "payments",
        format="{message}",
    )
    logger.add(
        BANK_WEBHOOK_LOG,
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "bank_webhooks",
        format="{message}",
    )
    logger.add(
        FEES_LOG,
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "fees",
        format="{message}",
    )
    _configured = True
