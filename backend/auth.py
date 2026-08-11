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
    client_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()
    now = datetime.now(timezone.utc)
    window = login_attempts[client_ip]
    while window and now - window[0] > timedelta(minutes=15):
        window.popleft()
    if len(window) >= 5:
        raise HTTPException(status_code=429, detail="Terlalu banyak percobaan. Coba lagi dalam 15 menit.")
    if email.lower().strip() != os.environ["ADMIN_EMAIL"].lower() or not hasher.verify(
        password, os.environ["ADMIN_PASSWORD_HASH"]
    ):
        window.append(now)
        raise HTTPException(status_code=401, detail="Email atau password salah")
    window.clear()
    return jwt.encode(
        {"sub": os.environ["ADMIN_EMAIL"], "exp": now + timedelta(minutes=30), "iat": now},
        os.environ["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Login admin diperlukan")
    try:
        payload = jwt.decode(credentials.credentials, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        if payload.get("sub") != os.environ["ADMIN_EMAIL"]:
            raise ValueError("invalid subject")
        return payload["sub"]
    except (jwt.InvalidTokenError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Sesi admin tidak valid atau telah berakhir") from error