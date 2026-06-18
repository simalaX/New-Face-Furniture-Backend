import os
import hmac
import hashlib
import time
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def _create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _verify_jwt(token: str | None) -> str | None:
    """Returns username if valid, None otherwise."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _get_token_from_request(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


# ─── Request schemas ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/login")
def login(data: LoginRequest):
    if (
        data.username != settings.ADMIN_USERNAME
        or data.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_jwt(data.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": data.username,
    }


@router.post("/logout")
def logout():
    # With JWT, logout is handled client-side by deleting the token
    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request):
    token = _get_token_from_request(request)
    username = _verify_jwt(token)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": username}


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, request: Request):
    token = _get_token_from_request(request)
    username = _verify_jwt(token)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if data.current_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../.env")
    )
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("ADMIN_PASSWORD="):
                new_lines.append(f"ADMIN_PASSWORD={data.new_password}\n")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"\nADMIN_PASSWORD={data.new_password}\n")

        with open(env_path, "w") as f:
            f.writelines(new_lines)

    except Exception:
        raise HTTPException(status_code=500, detail="Could not update password file")

    return {"message": "Password updated successfully."}