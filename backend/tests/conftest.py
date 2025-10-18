"""Shared test fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DISABLE_SCHEDULER", "1")

from app.api.deps import get_db
from app.core.middleware import reset_rate_limiter_sync
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.core.metrics import reset_metrics
from app.scheduler import shutdown_scheduler
from app.services import event_logger, notifications as notification_service
from app.services.chat import connection_manager as chat_connection_manager
from app.services.notifications import connection_manager as notification_connection_manager
from app.services import telegram as telegram_service

from app import models as _models  # noqa: F401  # ensure mappers are registered
from app.models import User

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

notification_service.SessionFactory = TestingSessionLocal
notification_connection_manager = notification_service.connection_manager
event_logger.SessionFactory = TestingSessionLocal
telegram_service.SessionLocal = TestingSessionLocal


def override_get_db():
    with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_session] = override_get_db


@pytest.fixture(autouse=True)
def prepare_database() -> None:
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        tables = {row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if 'admin_level' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN admin_level TEXT DEFAULT 'NONE'"))
            columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        conn.execute(text("PRAGMA foreign_keys=ON"))
    assert {"users", "event_logs", "messages", "telegram_links", "payments", "payouts", "transactions", "system_settings"}.issubset(tables)
    assert 'admin_level' in columns
    assert 'admin_level' in User.__table__.columns
    reset_rate_limiter_sync()
    reset_metrics()
    shutdown_scheduler()
    for path in (event_logger.LOG_FILE, event_logger.STATS_FILE):
        if path.exists():
            path.unlink()
    logs_dir = PROJECT_ROOT.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    chat_log = logs_dir / "chat.log"
    notification_log = logs_dir / "notifications.log"
    telegram_log = logs_dir / "telegram.log"
    payments_log = logs_dir / "payments.log"
    bank_log = logs_dir / "bank_webhooks.log"
    fees_log = logs_dir / "fees.log"
    for path in (chat_log, notification_log, telegram_log, payments_log, bank_log, fees_log):
        if path.exists():
            path.write_text("", encoding="utf-8")
        else:
            path.touch()
    backend_logs_dir = PROJECT_ROOT / "logs"
    backend_logs_dir.mkdir(parents=True, exist_ok=True)
    actions_backend_log = backend_logs_dir / "actions.log"
    actions_backend_log.write_text("", encoding="utf-8")
    chat_connection_manager.reset_sync()
    notification_connection_manager.reset_sync()


@pytest.fixture
def client(prepare_database) -> TestClient:  # type: ignore[func-returns-value]
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Session:
    with TestingSessionLocal() as session:
        yield session
