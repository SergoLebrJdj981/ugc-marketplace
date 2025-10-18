"""Telegram bot integration helpers."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
from loguru import logger

from app.core.config import settings, PROJECT_ROOT
from app.db.session import SessionLocal
from app.models import TelegramLink, User

LOG_DIR = PROJECT_ROOT.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
TELEGRAM_LOG_FILE = LOG_DIR / "telegram.log"
TELEGRAM_LOG_FILE.touch(exist_ok=True)

if not getattr(logger, "_telegram_sink_configured", False):  # type: ignore[attr-defined]
    logger.add(
        TELEGRAM_LOG_FILE,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["extra"].get("channel") == "telegram",
        format="{message}",
    )
    logger._telegram_sink_configured = True  # type: ignore[attr-defined]

telegram_logger = logger.bind(channel="telegram")


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def log_telegram_event(*, chat_id: str | int | None, message: str, status: str, error: str | None = None) -> None:
    pieces = [
        f"[TELEGRAM] [{_timestamp()}]",
        f"user={chat_id if chat_id is not None else 'unknown'}",
        f'msg="{message}"',
        f"status={status}",
    ]
    if error:
        pieces.append(f"error={error}")
    telegram_logger.info(" ".join(pieces))


async def send_telegram_message(chat_id: str | int, text: str) -> str:
    token = getattr(settings, "telegram_bot_token", None)
    api_base = getattr(settings, "telegram_api_url", "https://api.telegram.org").rstrip("/")

    if not token:
        log_telegram_event(chat_id=chat_id, message=text, status="skipped", error="bot_disabled")
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


def _save_link(
    *,
    user: User,
    session,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> None:
    existing_for_user = session.query(TelegramLink).filter(TelegramLink.user_id == user.id).one_or_none()
    existing_for_chat = session.query(TelegramLink).filter(TelegramLink.telegram_id == telegram_id).one_or_none()

    if existing_for_chat and existing_for_chat.user_id != user.id:
        existing_for_chat.user_id = user.id
        existing_for_chat.username = username
        existing_for_chat.first_name = first_name
        existing_for_chat.last_name = last_name
        existing_for_chat.is_active = True
    elif existing_for_user:
        existing_for_user.telegram_id = telegram_id
        existing_for_user.username = username
        existing_for_user.first_name = first_name
        existing_for_user.last_name = last_name
        existing_for_user.is_active = True
    else:
        session.add(
            TelegramLink(
                user_id=user.id,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
        )


async def _handle_start(session, chat_id: int, args: str | None, profile: dict[str, Any]) -> dict[str, Any]:
    if not args:
        text = "Добро пожаловать в UGC Marketplace! Используйте /profile или /balance для получения информации."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/start", status=status)
        return {"status": status, "response": text}

    try:
        user_id = UUID(args.strip())
    except ValueError:
        text = "Некорректный идентификатор. Откройте личный кабинет и повторите ссылку." if args else "Отсутствует идентификатор пользователя."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/start", status="invalid", error="bad_argument")
        return {"status": status, "response": text}

    user = session.get(User, user_id)
    if not user:
        text = "Пользователь не найден. Проверьте ссылку из личного кабинета."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/start", status="user_not_found")
        return {"status": status, "response": text}

    _save_link(
        user=user,
        session=session,
        telegram_id=chat_id,
        username=profile.get("username"),
        first_name=profile.get("first_name"),
        last_name=profile.get("last_name"),
    )
    session.commit()

    text = "Telegram успешно привязан ✅"
    status = await send_telegram_message(chat_id, text)
    log_telegram_event(chat_id=chat_id, message="/start", status="linked")
    return {"status": status, "response": text}


async def _handle_profile(session, chat_id: int) -> dict[str, Any]:
    link = (
        session.query(TelegramLink)
        .filter(TelegramLink.telegram_id == chat_id, TelegramLink.is_active.is_(True))
        .one_or_none()
    )
    if not link:
        text = "Telegram не привязан. Используйте кнопку в личном кабинете, чтобы связать аккаунт."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/profile", status="not_linked")
        return {"status": status, "response": text}

    user = session.get(User, link.user_id)
    profile_text = user.full_name or user.email or str(user.id)
    text = f"Профиль привязан: {profile_text}"
    status = await send_telegram_message(chat_id, text)
    log_telegram_event(chat_id=chat_id, message="/profile", status="linked")
    return {"status": status, "response": text}


async def _handle_balance(session, chat_id: int) -> dict[str, Any]:
    link = (
        session.query(TelegramLink)
        .filter(TelegramLink.telegram_id == chat_id, TelegramLink.is_active.is_(True))
        .one_or_none()
    )
    if not link:
        text = "Баланс доступен после привязки аккаунта."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/balance", status="not_linked")
        return {"status": status, "response": text}

    text = "Ваш текущий баланс: 5400₽ 💰"
    status = await send_telegram_message(chat_id, text)
    log_telegram_event(chat_id=chat_id, message="/balance", status="delivered")
    return {"status": status, "response": text}


async def _handle_unsubscribe(session, chat_id: int) -> dict[str, Any]:
    link = (
        session.query(TelegramLink)
        .filter(TelegramLink.telegram_id == chat_id, TelegramLink.is_active.is_(True))
        .one_or_none()
    )
    if not link:
        text = "Привязка не найдена."
        status = await send_telegram_message(chat_id, text)
        log_telegram_event(chat_id=chat_id, message="/unsubscribe", status="not_linked")
        return {"status": status, "response": text}

    link.is_active = False
    session.commit()
    text = "Вы успешно отписались от уведомлений 🔕"
    status = await send_telegram_message(chat_id, text)
    log_telegram_event(chat_id=chat_id, message="/unsubscribe", status="unsubscribed")
    return {"status": status, "response": text}


def _extract_message(payload: dict[str, Any]) -> tuple[int | None, str | None, dict[str, Any]]:
    message = payload.get("message") or payload.get("edited_message")
    if not isinstance(message, dict):
        return None, None, {}
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text")
    from_user = message.get("from", {})
    return chat_id, text, from_user


async def handle_telegram_update(payload: dict[str, Any]) -> dict[str, Any]:
    chat_id, text, profile = _extract_message(payload)
    if chat_id is None or not text:
        log_telegram_event(chat_id=chat_id, message=text or "", status="ignored", error="missing chat/text")
        return {"status": "ignored"}

    session = SessionLocal()
    try:
        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None

            if command == "/start":
                return await _handle_start(session, chat_id, args, profile)
            if command == "/profile":
                return await _handle_profile(session, chat_id)
            if command == "/balance":
                return await _handle_balance(session, chat_id)
            if command == "/unsubscribe":
                return await _handle_unsubscribe(session, chat_id)

            text = "Команда не распознана. Доступные команды: /start, /profile, /balance, /unsubscribe."
            status = await send_telegram_message(chat_id, text)
            log_telegram_event(chat_id=chat_id, message=command, status="unknown_command")
            return {"status": status, "response": text}

        status = await send_telegram_message(
            chat_id,
            "Сообщение получено. Используйте команды /start, /profile, /balance, /unsubscribe.",
        )
        log_telegram_event(chat_id=chat_id, message=text, status=status)
        return {"status": status}
    finally:
        session.close()


def handle_telegram_update_sync(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():  # pragma: no cover
        return loop.run_until_complete(handle_telegram_update(payload))
    return asyncio.run(handle_telegram_update(payload))


log_telegram_event(chat_id="system", message="logging initialized", status="ready")
