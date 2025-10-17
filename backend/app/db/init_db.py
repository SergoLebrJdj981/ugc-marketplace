"""Database initialisation and seed helpers."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import User

DEFAULT_USERS: tuple[dict[str, str], ...] = (
    {
        "email": "creator@example.com",
        "password": "Secret123!",
        "role": "creator",
        "full_name": "Demo Creator",
    },
    {
        "email": "slebronov@mail.ru",
        "password": "12322828",
        "role": "brand",
        "full_name": "Sergey Lebronov",
    },
    {
        "email": "admin@example.com",
        "password": "Secret123!",
        "role": "admin",
        "full_name": "Platform Admin",
    },
)


logger = logging.getLogger(__name__)


@contextmanager
def _session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - defensive rollback
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create missing tables and ensure demo accounts exist."""

    db_path: Path | None = None
    existed = False
    if engine.url.drivername.startswith("sqlite") and engine.url.database:
        db_path = Path(engine.url.database).resolve()
        existed = db_path.exists()
        db_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    if db_path and db_path.exists():
        message = "Database already initialised" if existed else "Database created"
        logger.info("%s at %s", message, db_path)

    with _session_scope() as session:
        for seed in DEFAULT_USERS:
            ensure_user(session, seed)


def ensure_user(session: Session, seed: dict[str, str]) -> None:
    """Create or update a demo user with a bcrypt password."""
    user = session.query(User).filter(User.email == seed["email"]).one_or_none()
    hashed_password = hash_password(seed["password"])
    if user:
        # Upgrade legacy hashes (non-bcrypt) and keep role/metadata aligned.
        if not user.password.startswith("$2") or not verify_password(seed["password"], user.password):
            user.password = hashed_password
        user.role = seed["role"]
        if seed.get("full_name"):
            user.full_name = seed["full_name"]
        return

    session.add(
        User(
            email=seed["email"],
            password=hashed_password,
            full_name=seed.get("full_name"),
            role=seed["role"],
            is_active=True,
        )
    )
