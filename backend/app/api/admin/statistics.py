"""Admin statistics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models import User
from app.models.enums import AdminLevel
from app.schemas import StatisticsResponse
from app.services import reports
from app.services.admin_logs import log_admin_action

router = APIRouter()


@router.get("", response_model=StatisticsResponse)
def get_statistics(
    *,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> StatisticsResponse:
    data = reports.generate_statistics(db)
    log_admin_action(db, str(admin_user.id), "view_statistics", None)
    return StatisticsResponse(data=data)


@router.get("/export", response_class=PlainTextResponse)
def export_statistics(
    *,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> PlainTextResponse:
    csv_content = reports.export_statistics_csv(db)
    log_admin_action(db, str(admin_user.id), "export_statistics", None)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=statistics.csv"},
    )
