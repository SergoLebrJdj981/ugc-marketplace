from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.middleware import setup_middleware
from app.scheduler import shutdown_scheduler, start_scheduler

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


@app.on_event("startup")
async def _start_scheduler() -> None:
    start_scheduler()


@app.on_event("shutdown")
async def _shutdown_scheduler() -> None:
    shutdown_scheduler()
