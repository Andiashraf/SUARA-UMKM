from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import List, Optional
import asyncio
import logging
import os
import re
import uuid

from alembic import command
from alembic.config import Config
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from database import AsyncSessionLocal, engine, get_db
from models import FanWallMessageModel, FanWallReactionModel


app = FastAPI(title="Portal HARNAS UMKM 2026 API")
api_router = APIRouter(prefix="/api")
ROOT_DIR = Path(__file__).parent


class FanWallMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
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
    avatar_url: str = Field(default="", max_length=500_000)

    @field_validator("full_name", "business_name", "role", "province", "city_regency", "message")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


SEED_MESSAGES = [
    {
        "id": "suara-1", "full_name": "Bahrul Ulum Ilham", "business_name": "ABDSI Indonesia",
        "role": "Pendamping BDS", "province": "Sulawesi Selatan", "city_regency": "Makassar",
        "message": "UMKM Indonesia tumbuh ketika pendampingan hadir dekat, konsisten, dan membuka jalan menuju pasar yang lebih luas.",
        "avatar_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=900&q=85",
        "likes_count": 248, "is_approved": True, "is_featured": True,
    },
    {
        "id": "suara-2", "full_name": "Ratna Wulandari", "business_name": "Kriya Pusaka Nusantara",
        "role": "Pelaku UMKM", "province": "DI Yogyakarta", "city_regency": "Bantul",
        "message": "Kami ingin produk lokal tidak hanya menjadi kebanggaan daerah, tetapi juga percaya diri berdiri di pasar dunia.",
        "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=900&q=85",
        "likes_count": 193, "is_approved": True, "is_featured": True,
    },
    {
        "id": "suara-3", "full_name": "Dimas Pratama", "business_name": "Kopi Lereng Khatulistiwa",
        "role": "Pelaku UMKM", "province": "Kalimantan Barat", "city_regency": "Pontianak",
        "message": "Kolaborasi lintas daerah membuat usaha kecil belajar lebih cepat, bertumbuh lebih sehat, dan menciptakan lebih banyak pekerjaan.",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=85",
        "likes_count": 171, "is_approved": True, "is_featured": True,
    },
    {
        "id": "suara-4", "full_name": "Prof. Maya Anggraini", "business_name": "Universitas Tanjungpura",
        "role": "Akademisi", "province": "Kalimantan Barat", "city_regency": "Pontianak",
        "message": "Riset kampus harus turun menjadi inovasi yang mudah dipakai pelaku UMKM, bukan berhenti sebagai laporan.",
        "avatar_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=900&q=85",
        "likes_count": 132, "is_approved": True, "is_featured": False,
    },
    {
        "id": "suara-5", "full_name": "Ahmad Firdaus", "business_name": "Dinas Koperasi dan UKM",
        "role": "Pemerintah", "province": "Jawa Barat", "city_regency": "Bandung",
        "message": "Kebijakan yang baik dimulai dengan mendengar pengalaman nyata pelaku usaha di lapangan.",
        "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=900&q=85",
        "likes_count": 117, "is_approved": True, "is_featured": False,
    },
    {
        "id": "suara-6", "full_name": "Sari Lestari", "business_name": "Forum Perempuan Berdaya",
        "role": "Lainnya", "province": "Jawa Timur", "city_regency": "Surabaya",
        "message": "Setiap usaha kecil menyimpan cerita keluarga, keberanian, dan masa depan yang layak diperjuangkan bersama.",
        "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=900&q=85",
        "likes_count": 99, "is_approved": True, "is_featured": False,
    },
]


async def seed_database() -> None:
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(func.count()).select_from(FanWallMessageModel))
        if count == 0:
            now = datetime.now(timezone.utc)
            session.add_all([FanWallMessageModel(**item, created_at=now) for item in SEED_MESSAGES])
            await session.commit()


def upgrade_database_schema() -> None:
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT_DIR / "alembic"))
    command.upgrade(config, "head")


@app.on_event("startup")
async def startup() -> None:
    await asyncio.to_thread(upgrade_database_schema)
    await seed_database()


@api_router.get("/")
async def root():
    return {"message": "Portal HARNAS UMKM 2026 API aktif", "database": "Supabase PostgreSQL"}


@api_router.get("/fan-wall", response_model=List[FanWallMessage])
async def list_messages(
    role: Optional[str] = None,
    province: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    sort: str = "newest",
    db: AsyncSession = Depends(get_db),
):
    statement = select(FanWallMessageModel).where(FanWallMessageModel.is_approved.is_(True))
    if role and role != "Semua":
        statement = statement.where(FanWallMessageModel.role == role)
    if province and province != "Semua Provinsi":
        statement = statement.where(FanWallMessageModel.province == province)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(or_(
            FanWallMessageModel.full_name.ilike(pattern),
            FanWallMessageModel.business_name.ilike(pattern),
            FanWallMessageModel.message.ilike(pattern),
        ))
    if sort == "popular":
        statement = statement.order_by(FanWallMessageModel.likes_count.desc(), FanWallMessageModel.created_at.desc())
    else:
        statement = statement.order_by(FanWallMessageModel.created_at.desc())
    result = await db.execute(statement.limit(200))
    return list(result.scalars().all())


@api_router.get("/fan-wall/stats")
async def fan_wall_stats(db: AsyncSession = Depends(get_db)):
    approved = FanWallMessageModel.is_approved.is_(True)
    voices = await db.scalar(select(func.count()).select_from(FanWallMessageModel).where(approved))
    provinces = await db.scalar(select(func.count(func.distinct(FanWallMessageModel.province))).where(approved))
    organizations = await db.scalar(select(func.count(func.distinct(FanWallMessageModel.business_name))).where(approved))
    supports = await db.scalar(select(func.coalesce(func.sum(FanWallMessageModel.likes_count), 0)).where(approved))
    return {"voices": voices or 0, "provinces": provinces or 0, "organizations": organizations or 0, "supports": supports or 0}


@api_router.post("/fan-wall", response_model=FanWallMessage, status_code=201)
async def submit_message(payload: FanWallMessageCreate, db: AsyncSession = Depends(get_db)):
    message = FanWallMessageModel(**payload.model_dump(), is_approved=False, is_featured=False, likes_count=0)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@api_router.post("/fan-wall/{message_id}/like")
async def like_message(message_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    message = await db.scalar(select(FanWallMessageModel).where(
        FanWallMessageModel.id == message_id, FanWallMessageModel.is_approved.is_(True)
    ))
    if not message:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")

    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    user_agent = request.headers.get("user-agent", "")[:160]
    voter_hash = sha256(f"{message_id}:{client_ip}:{user_agent}".encode()).hexdigest()
    db.add(FanWallReactionModel(message_id=message_id, voter_hash=voter_hash))
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        current = await db.scalar(select(FanWallMessageModel).where(FanWallMessageModel.id == message_id))
        return {"id": current.id, "likes_count": current.likes_count, "already_liked": True}

    result = await db.execute(
        update(FanWallMessageModel)
        .where(FanWallMessageModel.id == message_id)
        .values(likes_count=FanWallMessageModel.likes_count + 1)
        .returning(FanWallMessageModel.id, FanWallMessageModel.likes_count)
    )
    liked_id, likes_count = result.one()
    await db.commit()
    return {"id": liked_id, "likes_count": likes_count, "already_liked": False}


app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@app.on_event("shutdown")
async def shutdown_database():
    await engine.dispose()