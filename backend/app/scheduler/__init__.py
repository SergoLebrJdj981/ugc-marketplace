"""Async scheduler setup for recurring maintenance jobs."""

from __future__ import annotations

from contextlib import suppress

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.cron_jobs import register_jobs

scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> None:
    """Start the global AsyncIO scheduler if it is not already running."""

    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone="UTC")
        register_jobs(scheduler)
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler() -> None:
    """Gracefully stop the scheduler."""

    global scheduler
    with suppress(Exception):
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)
