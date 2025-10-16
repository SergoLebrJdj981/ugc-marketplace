from fastapi import FastAPI
from pydantic import BaseModel

from app.api import api_router
from app.core.error_handlers import register_exception_handlers
from app.core.middleware import setup_middleware

app = FastAPI(title="UGC Marketplace API", version="0.3.0")
setup_middleware(app)
register_exception_handlers(app)
app.include_router(api_router)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def read_health() -> HealthResponse:
    """Return a simple health payload for smoke tests."""

    return HealthResponse(status="ok", service="backend")
