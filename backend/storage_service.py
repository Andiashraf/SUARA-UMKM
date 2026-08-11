from io import BytesIO
from pathlib import Path
import asyncio
import os
import uuid

from dotenv import load_dotenv
from fastapi import HTTPException
from PIL import Image
from supabase import Client, create_client


load_dotenv(Path(__file__).parent / ".env")
MAX_AVATAR_SIZE = 1_000_000
MIME_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def _client() -> Client:
    secret = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not secret:
        raise HTTPException(status_code=503, detail="Supabase Storage belum dikonfigurasi oleh administrator")
    return create_client(os.environ["SUPABASE_URL"], secret)


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
    path = f"avatars/{uuid.uuid4()}.{extension}"
    bucket = os.environ.get("STORAGE_BUCKET", "fan-wall-avatars")

    def upload() -> str:
        client = _client()
        client.storage.from_(bucket).upload(
            path,
            raw,
            {"content-type": mime, "cache-control": "31536000", "upsert": "false"},
        )
        return client.storage.from_(bucket).get_public_url(path)

    try:
        return path, await asyncio.to_thread(upload)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="Upload foto ke Supabase Storage gagal") from error


async def remove_avatar(path: str | None) -> None:
    if not path:
        return

    def remove() -> None:
        client = _client()
        client.storage.from_(os.environ.get("STORAGE_BUCKET", "fan-wall-avatars")).remove([path])

    try:
        await asyncio.to_thread(remove)
    except Exception:
        return