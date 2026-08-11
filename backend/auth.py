from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash


load_dotenv(Path(__file__).parent / ".env")
security = HTTPBearer(auto_error=False)
hasher = PasswordHash.recommended()
login_attempts: dict[str, deque] = defaultdict(deque)


def authenticate_admin(email: str, password: str, request: Request) -> str:
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@harnassuaraumkm.id")
    admin_password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "$argon2id$v=19$m=65536,t=3,p=4$defaultsalt$defaulthash")
    jwt_secret = os.environ.get("JWT_SECRET_KEY", "harnas-umkm-jwt-secret-key-2026")

    client_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()
    now = datetime.now(timezone.utc)
    window = login_attempts[client_ip]
    while window and now - window[0] > timedelta(minutes=15):
        window.popleft()
    if len(window) >= 5:
        raise HTTPException(status_code=429, detail="Terlalu banyak percobaan. Coba lagi dalam 15 menit.")
    if email.lower().strip() != admin_email.lower() or not hasher.verify(
        password, admin_password_hash
    ):
        window.append(now)
        raise HTTPException(status_code=401, detail="Email atau password salah")
    window.clear()
    return jwt.encode(
        {"sub": admin_email, "exp": now + timedelta(minutes=30), "iat": now},
        jwt_secret,
        algorithm="HS256",
    )


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Login admin diperlukan")
    jwt_secret = os.environ.get("JWT_SECRET_KEY", "harnas-umkm-jwt-secret-key-2026")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@harnassuaraumkm.id")
    try:
        payload = jwt.decode(credentials.credentials, jwt_secret, algorithms=["HS256"])
        if payload.get("sub") != admin_email:
            raise ValueError("invalid subject")
        return payload["sub"]
    except (jwt.InvalidTokenError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Sesi admin tidak valid atau telah berakhir") from error