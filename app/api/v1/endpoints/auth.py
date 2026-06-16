import os
import hmac
import hashlib
import time
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

# ─── Token helpers ────────────────────────────────────────────────────────────
# Instead of storing the plaintext string "true", we store a signed token:
#   {timestamp}:{hmac_signature}
# This means even if someone sets the cookie manually they cannot forge it
# without knowing the SECRET_KEY.

def _make_token() -> str:
    """Generate a time-stamped HMAC token."""
    ts = str(int(time.time()))
    secret = settings.SECRET_KEY.encode()
    sig = hmac.new(secret, ts.encode(), hashlib.sha256).hexdigest()
    return f"{ts}:{sig}"

def _verify_token(token: str | None) -> bool:
    """Return True only if token is a valid, unexpired HMAC token."""
    if not token:
        return False
    try:
        ts_str, sig = token.split(":", 1)
        ts = int(ts_str)
    except (ValueError, AttributeError):
        return False

    # Recompute expected signature
    secret = settings.SECRET_KEY.encode()
    expected = hmac.new(secret, ts_str.encode(), hashlib.sha256).hexdigest()

    # Constant-time compare to prevent timing attacks
    if not hmac.compare_digest(expected, sig):
        return False

    # Expire after 24 hours
    if time.time() - ts > 86400:
        return False

    return True


# ─── Request / Response schemas ───────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/login")
def login(data: LoginRequest, response: Response):
    if (
        data.username != settings.ADMIN_USERNAME
        or data.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _make_token()

    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,          # JS cannot read this cookie
        samesite="lax",
        secure=False,           # set True in production with HTTPS
        max_age=86400,          # 24 hours
        path="/",
    )
    return {"message": "Login successful", "username": data.username}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("admin_session", path="/")
    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request):
    token = request.cookies.get("admin_session")
    if not _verify_token(token):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": settings.ADMIN_USERNAME}


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, request: Request):
    token = request.cookies.get("admin_session")
    if not _verify_token(token):
        raise HTTPException(status_code=401, detail="Not authenticated")

    if data.current_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    # Update the .env file
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

    return {"message": "Password updated. Restart the server to apply."}