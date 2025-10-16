"""Utility helpers for recording admin actions."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.admin_log import AdminLog


def _serialise_metadata(metadata: dict[str, Any] | None) -> str:
    if not metadata:
        return "{}"
    return json.dumps(metadata, default=str)


def log_admin_action(db: Session, admin_id: str | None, action: str, target_id: str | None = None, metadata: dict[str, Any] | None = None) -> None:
    entry = AdminLog(admin_id=admin_id, action=action, target_id=target_id, details=_serialise_metadata(metadata))
    db.add(entry)
    db.commit()
