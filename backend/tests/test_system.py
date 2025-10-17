from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/system/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint(client: TestClient) -> None:
    # Generate some traffic
    client.get("/api/system/health")
    client.post("/api/webhooks/bank", json={"event": "metrics_run"})

    response = client.get("/api/system/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime" in data
    assert "requests_per_min" in data
    assert "errors" in data
    assert "total_events" in data
    assert isinstance(data["recent_events"], list)
