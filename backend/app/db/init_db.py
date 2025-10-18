"""Database initialisation and seed helpers."""

from __future__ import annotations

import logging
from decimal import Decimal
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import AdminLevel, SystemSetting, User

DEFAULT_USERS: tuple[dict[str, object], ...] = (
    {
        "email": "creator@example.com",
        "password": "Secret123!",
        "role": "creator",
        "full_name": "Demo Creator",
        "admin_level": AdminLevel.NONE,
    },
    {
        "email": "slebronov@mail.ru",
        "password": "12322828",
        "role": "brand",
        "full_name": "Sergey Lebronov",
        "admin_level": AdminLevel.NONE,
    },
    {
        "email": "admin@example.com",
        "password": "Secret123!",
        "role": "admin",
        "full_name": "Platform Admin",
        "admin_level": AdminLevel.ADMIN_LEVEL_3,
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
        _ensure_admin_level_column(session)
        for seed in DEFAULT_USERS:
            ensure_user(session, seed)
        ensure_platform_fee(session)


def _ensure_admin_level_column(session: Session) -> None:
    inspector = inspect(session.bind)
    columns = {column['name'] for column in inspector.get_columns('users')}
    if 'admin_level' not in columns:
        session.execute(text("ALTER TABLE users ADD COLUMN admin_level VARCHAR(32) DEFAULT 'NONE'"))
    session.execute(text("UPDATE users SET admin_level = 'NONE' WHERE admin_level IS NULL OR lower(admin_level) = 'none'"))


def ensure_user(session: Session, seed: dict[str, object]) -> None:
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
        if seed.get("admin_level"):
            user.admin_level = seed["admin_level"]  # type: ignore[assignment]
        return

    session.add(
        User(
            email=seed["email"],
            password=hashed_password,
            full_name=seed.get("full_name"),
            role=seed["role"],
            is_active=True,
            admin_level=seed.get("admin_level", AdminLevel.NONE),  # type: ignore[arg-type]
        )
    )


def ensure_platform_fee(session: Session) -> None:
    """Ensure the default platform fee exists."""
    _ensure_setting(
        session,
        key="platform_fee",
        default_value=Decimal("0.10"),
        default_description="10% комиссия платформы",
    )
    _ensure_setting(
        session,
        key="platform_fee_deposit",
        default_value=Decimal("0.10"),
        default_description="Комиссия платформы при депозите (10%)",
    )
    _ensure_setting(
        session,
        key="platform_fee_payout",
        default_value=Decimal("0.10"),
        default_description="Комиссия платформы при выплатах (10%)",
    )


def _ensure_setting(session: Session, *, key: str, default_value: Decimal, default_description: str) -> None:
    setting = session.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
    if setting is None:
        session.add(
            SystemSetting(
                key=key,
                value=default_value,
                description=default_description,
            )
        )
        return

    if setting.value is None:
        setting.value = default_value
    if not setting.description:
        setting.description = default_description
