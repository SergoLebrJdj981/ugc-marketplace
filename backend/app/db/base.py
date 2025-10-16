"""Declarative metadata for Alembic autogenerate support."""

from app.db.session import Base

# Import all models here so Alembic's autogenerate can discover them
from app.models.user import User  # noqa: F401
from app.models.campaign import Campaign  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.video import Video  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.rating import Rating  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.notification import Notification  # noqa: F401
