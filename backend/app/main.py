from fastapi import FastAPI
from pydantic import BaseModel

from app.api import api_router
from app.core.error_handlers import register_exception_handlers

app = FastAPI(title="UGC Marketplace API", version="0.2.0")
register_exception_handlers(app)
app.include_router(api_router)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def read_health() -> HealthResponse:
    """Return a simple health payload for smoke tests."""

    return HealthResponse(status="ok", service="backend")
