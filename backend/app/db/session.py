"""Database session and engine management."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import PROJECT_ROOT, settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def _ensure_sqlite_database(url_str: str) -> str:
    url = make_url(url_str)
    if not url.drivername.startswith("sqlite"):
        return url_str

    if url.database is None:
        return url_str

    db_path = Path(url.database)
    if not db_path.is_absolute():
        db_path = (PROJECT_ROOT / db_path).resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        db_path.touch()

    url = url.set(database=str(db_path))
    return url.render_as_string(hide_password=False)


DATABASE_URL = _ensure_sqlite_database(settings.database_url)
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session():
    """Yield a transactional SQLAlchemy session."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
