"""Shared API dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_session


def get_db() -> Generator[Session, None, None]:
    """Provide a database session to request scope."""

    yield from get_session()
