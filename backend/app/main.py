from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="UGC Marketplace API", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    """Return a simple health payload for smoke tests."""
    return HealthResponse(status="ok", service="backend")
