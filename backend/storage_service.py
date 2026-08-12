from io import BytesIO
from pathlib import Path
import asyncio
import os
import uuid

from fastapi import HTTPException
from PIL import Image

MAX_AVATAR_SIZE = 1_000_000
MIME_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

UPLOADS_DIR = Path(__file__).parent / "uploads" / "avatars"
os.makedirs(UPLOADS_DIR, exist_ok=True)

def validate_image(raw: bytes, declared_mime: str) -> tuple[str, str]:
    if len(raw) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=413, detail="Foto profil maksimal 1 MB")
    try:
        with Image.open(BytesIO(raw)) as image:
            image.verify()
        with Image.open(BytesIO(raw)) as image:
            actual_mime = Image.MIME.get(image.format)
    except Exception as error:
        raise HTTPException(status_code=415, detail="File bukan gambar yang valid") from error
    if declared_mime not in MIME_EXTENSIONS or actual_mime not in MIME_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Gunakan gambar JPEG, PNG, atau WebP")
    if declared_mime != actual_mime:
        raise HTTPException(status_code=415, detail="Format file tidak sesuai dengan isi gambar")
    return actual_mime, MIME_EXTENSIONS[actual_mime]

async def upload_avatar(raw: bytes, declared_mime: str) -> tuple[str, str]:
    mime, extension = validate_image(raw, declared_mime)
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = UPLOADS_DIR / filename
    
    def save_file():
        with open(filepath, "wb") as f:
            f.write(raw)
            
    try:
        await asyncio.to_thread(save_file)
        # Return path and the public URL that FastAPI will serve
        public_url = f"/api/static/avatars/{filename}"
        return f"avatars/{filename}", public_url
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="Gagal menyimpan foto di server") from error

async def remove_avatar(path: str | None) -> None:
    if not path:
        return
    try:
        filepath = UPLOADS_DIR.parent / path
        if filepath.exists():
            os.remove(filepath)
    except Exception:
        return