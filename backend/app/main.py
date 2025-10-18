import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.api.chat import ws_router as chat_ws_router
from app.api.notifications import ws_router as notifications_ws_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.db.init_db import init_db
from app.scheduler import shutdown_scheduler, start_scheduler

logger = logging.getLogger(__name__)

setup_logging()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

register_exception_handlers(app)
setup_middleware(app)
app.include_router(api_router)
app.include_router(chat_ws_router)
app.include_router(notifications_ws_router)


@app.on_event("startup")
async def _on_startup() -> None:
    init_db()
    start_scheduler()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def _shutdown_scheduler() -> None:
    shutdown_scheduler()
