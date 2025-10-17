from fastapi.testclient import TestClient


def test_register_and_login_flow(client: TestClient) -> None:
    register_payload = {
        "email": "test-user@example.com",
        "password": "Secret123!",
        "full_name": "Test User",
        "role": "brand",
    }
    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201
    payload = register_response.json()
    assert payload["user"]["email"] == register_payload["email"]
    assert payload["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == register_payload["email"]


def test_refresh_token(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "Secret123!",
            "full_name": "Refresh User",
            "role": "creator",
        },
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "refresh@example.com", "password": "Secret123!"},
    )
    tokens = login_response.json()
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
