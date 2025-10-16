"""Security and middleware behaviour tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_rate_limiter_enforces_limit(client: TestClient) -> None:
    for idx in range(61):
        response = client.get("/health")
        if idx < 60:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert response.json()["message"] == "Too many requests"


def test_cors_headers(client: TestClient) -> None:
    allowed = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert allowed.status_code == 200
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    blocked = client.get("/health", headers={"Origin": "http://evil.example"})
    assert blocked.status_code == 200
    assert "access-control-allow-origin" not in blocked.headers
