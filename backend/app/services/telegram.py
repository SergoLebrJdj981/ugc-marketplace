"""Telegram bot integration helpers."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings

telegram_logger = logger.bind(channel="telegram")


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def log_telegram_event(*, chat_id: str | int | None, message: str, status: str, error: str | None = None) -> None:
    pieces = [
        f"[TG] [{_timestamp()}]",
        f"chat={chat_id if chat_id is not None else 'unknown'}",
        f'"{message}"',
        f"status={status}",
    ]
    if error:
        pieces.append(f"error={error}")
    telegram_logger.info(" ".join(pieces))


async def send_telegram_message(chat_id: str | int, text: str) -> str:
    token = getattr(settings, "telegram_bot_token", None)
    api_base = getattr(settings, "telegram_api_url", "https://api.telegram.org").rstrip("/")

    if not token:
        log_telegram_event(chat_id=chat_id, message=text, status="skipped", error="no token configured")
        return "skipped"

    url = f"{api_base}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if not data.get("ok", False):
                raise ValueError(str(data))
        log_telegram_event(chat_id=chat_id, message=text, status="delivered")
        return "delivered"
    except Exception as exc:  # pragma: no cover - network dependent
        log_telegram_event(chat_id=chat_id, message=text, status="failed", error=str(exc))
        return "failed"


async def _handle_command(chat_id: str | int, command: str, args: str | None) -> dict[str, Any]:
    command = command.lower()
    if command == "/start":
        text = "Добро пожаловать в UGC Marketplace! Используйте /profile или /balance для получения информации."
    elif command == "/profile":
        text = "Профиль пользователя недоступен в демо-режиме. Авторизуйтесь в веб-интерфейсе."
    elif command == "/balance":
        text = "Баланс будет доступен после подключения финансового модуля."
    else:
        text = "Команда не распознана. Доступные команды: /start, /profile, /balance."

    status = await send_telegram_message(chat_id, text)
    log_telegram_event(chat_id=chat_id, message=text, status=status)
    return {"status": status, "response": text}


def _extract_text(payload: dict[str, Any]) -> tuple[str | int | None, str | None]:
    message = payload.get("message") or payload.get("edited_message")
    if not message:
        return None, None
    if isinstance(message, dict):
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text")
        return chat_id, text
    if isinstance(message, str):
        return None, message
    return None, None


async def handle_telegram_update(payload: dict[str, Any]) -> dict[str, Any]:
    chat_id, text = _extract_text(payload)
    if chat_id is None or not text:
        log_telegram_event(chat_id=chat_id, message=text or "", status="ignored", error="missing chat/text")
        return {"status": "ignored"}

    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else None
        return await _handle_command(chat_id, command, args)

    status = await send_telegram_message(
        chat_id,
        "Сообщение получено. Используйте команды /start, /profile, /balance.",
    )
    log_telegram_event(chat_id=chat_id, message=text, status=status)
    return {"status": status}


def handle_telegram_update_sync(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():  # pragma: no cover
        return loop.run_until_complete(handle_telegram_update(payload))
    return asyncio.run(handle_telegram_update(payload))
