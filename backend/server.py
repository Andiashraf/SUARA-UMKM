from datetime import datetime, timezone
from hashlib import sha256
from typing import List, Optional
import asyncio
import logging
import os
import re
import uuid

from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.middleware.cors import CORSMiddleware

from admin_routes import router as admin_router
from database import get_db, row_to_dict, rows_to_dicts
from migrations import migrate_and_seed
from storage_service import upload_avatar


app = FastAPI(title="Portal HARNAS UMKM 2026 API")
api_router = APIRouter(prefix="/api")


class FanWallMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    business_name: str
    role: str
    province: str
    city_regency: str = ""
    message: str
    avatar_url: str = ""
    likes_count: int = 0
    is_approved: bool = False
    is_featured: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FanWallMessageCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=80)
    business_name: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=50)
    province: str = Field(min_length=2, max_length=50)
    city_regency: str = Field(default="", max_length=80)
    message: str = Field(min_length=20, max_length=800)
    avatar_url: str = Field(default="", max_length=2_000)
    avatar_path: Optional[str] = Field(default=None, max_length=500)

    @field_validator("full_name", "business_name", "role", "province", "city_regency", "message")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


SEED_MESSAGES = [
    {"id": "suara-1", "full_name": "Bahrul Ulum Ilham", "business_name": "ABDSI Indonesia", "role": "Pendamping BDS", "province": "Sulawesi Selatan", "city_regency": "Makassar", "message": "UMKM Indonesia tumbuh ketika pendampingan hadir dekat, konsisten, dan membuka jalan menuju pasar yang lebih luas.", "avatar_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=900&q=85", "likes_count": 248, "is_featured": True},
    {"id": "suara-2", "full_name": "Ratna Wulandari", "business_name": "Kriya Pusaka Nusantara", "role": "Pelaku UMKM", "province": "DI Yogyakarta", "city_regency": "Bantul", "message": "Kami ingin produk lokal tidak hanya menjadi kebanggaan daerah, tetapi juga percaya diri berdiri di pasar dunia.", "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=900&q=85", "likes_count": 193, "is_featured": True},
    {"id": "suara-3", "full_name": "Dimas Pratama", "business_name": "Kopi Lereng Khatulistiwa", "role": "Pelaku UMKM", "province": "Kalimantan Barat", "city_regency": "Pontianak", "message": "Kolaborasi lintas daerah membuat usaha kecil belajar lebih cepat, bertumbuh lebih sehat, dan menciptakan lebih banyak pekerjaan.", "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=85", "likes_count": 171, "is_featured": True},
    {"id": "suara-4", "full_name": "Prof. Maya Anggraini", "business_name": "Universitas Tanjungpura", "role": "Akademisi", "province": "Kalimantan Barat", "city_regency": "Pontianak", "message": "Riset kampus harus turun menjadi inovasi yang mudah dipakai pelaku UMKM, bukan berhenti sebagai laporan.", "avatar_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=900&q=85", "likes_count": 132, "is_featured": False},
    {"id": "suara-5", "full_name": "Ahmad Firdaus", "business_name": "Dinas Koperasi dan UKM", "role": "Pemerintah", "province": "Jawa Barat", "city_regency": "Bandung", "message": "Kebijakan yang baik dimulai dengan mendengar pengalaman nyata pelaku usaha di lapangan.", "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=900&q=85", "likes_count": 117, "is_featured": False},
    {"id": "suara-6", "full_name": "Sari Lestari", "business_name": "Forum Perempuan Berdaya", "role": "Lainnya", "province": "Jawa Timur", "city_regency": "Surabaya", "message": "Setiap usaha kecil menyimpan cerita keluarga, keberanian, dan masa depan yang layak diperjuangkan bersama.", "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=900&q=85", "likes_count": 99, "is_featured": False},
]


@app.on_event("startup")
async def startup() -> None:
    await asyncio.to_thread(migrate_and_seed, SEED_MESSAGES)


@api_router.get("/")
def root():
    return {"message": "Portal HARNAS UMKM 2026 API aktif", "database": "Turso/libSQL"}


@api_router.get("/fan-wall", response_model=List[FanWallMessage])
def list_messages(
    role: Optional[str] = None,
    province: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    sort: str = "newest",
    db=Depends(get_db),
):
    conditions, params = ["moderation_status = 'approved'"], []
    if role and role != "Semua":
        conditions.append("role = ?"); params.append(role)
    if province and province != "Semua Provinsi":
        conditions.append("province = ?"); params.append(province)
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append("(LOWER(full_name) LIKE LOWER(?) OR LOWER(business_name) LIKE LOWER(?) OR LOWER(message) LIKE LOWER(?))")
        params.extend([pattern, pattern, pattern])
    order = "likes_count DESC, created_at DESC" if sort == "popular" else "is_featured DESC, created_at DESC"
    cursor = db.execute(f"SELECT * FROM fan_wall_messages WHERE {' AND '.join(conditions)} ORDER BY {order} LIMIT 200", tuple(params))
    return rows_to_dicts(cursor)


@api_router.get("/fan-wall/stats")
def fan_wall_stats(db=Depends(get_db)):
    voices, provinces, organizations, supports = db.execute(
        """SELECT COUNT(*), COUNT(DISTINCT province), COUNT(DISTINCT business_name),
           COALESCE(SUM(likes_count), 0) FROM fan_wall_messages
           WHERE moderation_status = 'approved'"""
    ).fetchone()
    return {"voices": voices, "provinces": provinces, "organizations": organizations, "supports": supports}


@api_router.post("/fan-wall", response_model=FanWallMessage, status_code=201)
def submit_message(payload: FanWallMessageCreate, db=Depends(get_db)):
    message_id, now = str(uuid.uuid4()), datetime.now(timezone.utc).isoformat()
    values = payload.model_dump()
    db.execute(
        """INSERT INTO fan_wall_messages (
            id, full_name, business_name, role, province, city_regency, message,
            avatar_url, avatar_path, likes_count, is_approved, is_featured,
            moderation_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 'pending', ?, ?)""",
        (message_id, values["full_name"], values["business_name"], values["role"], values["province"], values["city_regency"], values["message"], values["avatar_url"], values["avatar_path"], now, now),
    )
    db.commit()
    cursor = db.execute("SELECT * FROM fan_wall_messages WHERE id = ?", (message_id,))
    return row_to_dict(cursor, cursor.fetchone())


@api_router.post("/uploads/avatar")
async def upload_profile_avatar(file: UploadFile = File(...)):
    raw = await file.read(1_000_001)
    avatar_path, avatar_url = await upload_avatar(raw, file.content_type or "")
    return {"avatar_path": avatar_path, "avatar_url": avatar_url}


@api_router.post("/fan-wall/{message_id}/like")
def like_message(message_id: str, request: Request, db=Depends(get_db)):
    cursor = db.execute("SELECT * FROM fan_wall_messages WHERE id = ? AND moderation_status = 'approved'", (message_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    user_agent = request.headers.get("user-agent", "")[:160]
    voter_hash = sha256(f"{message_id}:{client_ip}:{user_agent}".encode()).hexdigest()
    reaction_id = str(uuid.uuid4())
    db.execute(
        "INSERT OR IGNORE INTO fan_wall_reactions (id, message_id, voter_hash, created_at) VALUES (?, ?, ?, ?)",
        (reaction_id, message_id, voter_hash, datetime.now(timezone.utc).isoformat()),
    )
    inserted = db.execute("SELECT changes()").fetchone()[0] == 1
    if inserted:
        db.execute("UPDATE fan_wall_messages SET likes_count = likes_count + 1 WHERE id = ?", (message_id,))
    db.commit()
    likes = db.execute("SELECT likes_count FROM fan_wall_messages WHERE id = ?", (message_id,)).fetchone()[0]
    return {"id": message_id, "likes_count": likes, "already_liked": not inserted}


app.include_router(api_router)
app.include_router(admin_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")