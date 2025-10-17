"""Authentication endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/auth")

FAKE_USER = {
    "email": "slebronov@mail.ru",
    "password": "12322828",
    "full_name": "Demo User",
    "role": "admin",
    "id": "demo-user-id",
}


@router.post("/login")
def login(payload: dict[str, str]):
    if payload.get("email") != FAKE_USER["email"] or payload.get("password") != FAKE_USER["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    claims = {"sub": FAKE_USER["id"], "role": FAKE_USER["role"], "email": FAKE_USER["email"]}
    access = create_access_token(claims)
    refresh = create_refresh_token(claims)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {
            "id": FAKE_USER["id"],
            "email": FAKE_USER["email"],
            "full_name": FAKE_USER["full_name"],
            "role": FAKE_USER["role"],
            "created_at": datetime.utcnow().isoformat(),
        },
    }


@router.post("/refresh")
def refresh(payload: dict[str, str]):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")
    data = verify_token(token, expected_type="refresh")
    new_access = create_access_token({k: data[k] for k in ("sub", "role")})
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"status": "ok"}
