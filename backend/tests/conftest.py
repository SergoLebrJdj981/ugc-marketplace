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

from app import models as _models  # noqa: F401  # ensure mappers are registered

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

notification_service.SessionFactory = TestingSessionLocal
event_logger.SessionFactory = TestingSessionLocal


def override_get_db():
    with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_session] = override_get_db


@pytest.fixture(autouse=True)
def prepare_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        tables = {row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
    assert {"users", "event_logs"}.issubset(tables)
    reset_rate_limiter_sync()
    reset_metrics()
    shutdown_scheduler()
    for path in (event_logger.LOG_FILE, event_logger.STATS_FILE):
        if path.exists():
            path.unlink()


@pytest.fixture
def client(prepare_database) -> TestClient:  # type: ignore[func-returns-value]
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Session:
    with TestingSessionLocal() as session:
        yield session
