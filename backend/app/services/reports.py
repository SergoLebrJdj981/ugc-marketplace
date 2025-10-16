"""Reporting utilities for admin dashboards."""

from __future__ import annotations

import csv
from io import StringIO

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Campaign, Order, Payment, User


def generate_user_report(db: Session) -> dict:
    role_counts = dict(db.execute(select(User.role, func.count()).group_by(User.role)).all())
    admin_levels = dict(db.execute(select(User.admin_level, func.count()).group_by(User.admin_level)).all())
    return {
        "roles": {role.value: count for role, count in role_counts.items()},
        "admin_levels": {level.value: count for level, count in admin_levels.items()},
    }


def generate_campaign_report(db: Session) -> dict:
    status_counts = dict(db.execute(select(Campaign.status, func.count()).group_by(Campaign.status)).all())
    top_brands = db.execute(
        select(Campaign.brand_id, func.count())
        .group_by(Campaign.brand_id)
        .order_by(func.count().desc())
        .limit(5)
    ).all()
    return {
        "status": {status.value: count for status, count in status_counts.items()},
        "top_brands": [
            {"brand_id": str(brand_id), "campaigns": total}
            for brand_id, total in top_brands
        ],
    }


def generate_finance_report(db: Session) -> dict:
    payment_counts = dict(db.execute(select(Payment.status, func.count()).group_by(Payment.status)).all())
    payment_totals = dict(
        db.execute(
            select(Payment.status, func.coalesce(func.sum(Payment.amount), 0)).group_by(Payment.status)
        ).all()
    )
    top_creators = db.execute(
        select(Order.creator_id, func.count())
        .group_by(Order.creator_id)
        .order_by(func.count().desc())
        .limit(5)
    ).all()
    return {
        "payments": {status.value: count for status, count in payment_counts.items()},
        "amounts": {status.value: str(total) for status, total in payment_totals.items()},
        "top_creators": [
            {"creator_id": str(creator_id), "orders": total}
            for creator_id, total in top_creators
        ],
    }


def generate_statistics(db: Session) -> dict:
    users_total = db.scalar(select(func.count()).select_from(User)) or 0
    campaigns_total = db.scalar(select(func.count()).select_from(Campaign)) or 0
    payments_total = db.scalar(select(func.count()).select_from(Payment)) or 0
    orders_total = db.scalar(select(func.count()).select_from(Order)) or 0

    return {
        "totals": {
            "users": users_total,
            "campaigns": campaigns_total,
            "payments": payments_total,
            "orders": orders_total,
        },
        "users": generate_user_report(db),
        "campaigns": generate_campaign_report(db),
        "finance": generate_finance_report(db),
    }


def export_statistics_csv(db: Session) -> str:
    stats = generate_statistics(db)
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    writer.writerow(["Section", "Key", "Value"])
    for section, data in stats.items():
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        writer.writerow([section, f"{key}.{subkey}", subvalue])
                else:
                    writer.writerow([section, key, value])
        else:
            writer.writerow([section, "value", data])

    return csv_buffer.getvalue()
