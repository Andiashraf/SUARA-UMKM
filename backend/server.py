from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import List, Optional
import logging
import os
import re
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.middleware.cors import CORSMiddleware


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]
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


@app.on_event("startup")
async def seed_database():
    await db.fan_wall_messages.create_index("id", unique=True)
    await db.fan_wall_messages.create_index([("is_approved", 1), ("created_at", -1)])
    await db.fan_wall_reactions.create_index([("message_id", 1), ("voter_hash", 1)], unique=True)
    if await db.fan_wall_messages.count_documents({}) == 0:
        now = datetime.now(timezone.utc).isoformat()
        await db.fan_wall_messages.insert_many([{**item, "created_at": now} for item in SEED_MESSAGES])


@api_router.get("/")
async def root():
    return {"message": "Portal HARNAS UMKM 2026 API aktif"}


@api_router.get("/fan-wall", response_model=List[FanWallMessage])
async def list_messages(
    role: Optional[str] = None,
    province: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    sort: str = "newest",
):
    query = {"is_approved": True}
    if role and role != "Semua":
        query["role"] = role
    if province and province != "Semua Provinsi":
        query["province"] = province
    if search:
        safe = re.escape(search.strip())
        query["$or"] = [
            {"full_name": {"$regex": safe, "$options": "i"}},
            {"business_name": {"$regex": safe, "$options": "i"}},
            {"message": {"$regex": safe, "$options": "i"}},
        ]
    order = [("likes_count", -1)] if sort == "popular" else [("created_at", -1)]
    docs = await db.fan_wall_messages.find(query, {"_id": 0}).sort(order).to_list(200)
    return docs


@api_router.get("/fan-wall/stats")
async def fan_wall_stats():
    voices = await db.fan_wall_messages.count_documents({"is_approved": True})
    provinces = await db.fan_wall_messages.distinct("province", {"is_approved": True})
    organizations = await db.fan_wall_messages.distinct("business_name", {"is_approved": True})
    likes = await db.fan_wall_messages.aggregate([
        {"$match": {"is_approved": True}}, {"$group": {"_id": None, "total": {"$sum": "$likes_count"}}}
    ]).to_list(1)
    return {"voices": voices, "provinces": len(provinces), "organizations": len(organizations), "supports": likes[0]["total"] if likes else 0}


@api_router.post("/fan-wall", response_model=FanWallMessage, status_code=201)
async def submit_message(payload: FanWallMessageCreate):
    message = FanWallMessage(**payload.model_dump())
    doc = message.model_dump()
    doc["created_at"] = message.created_at.isoformat()
    await db.fan_wall_messages.insert_one(doc)
    return message


@api_router.post("/fan-wall/{message_id}/like")
async def like_message(message_id: str, request: Request):
    existing = await db.fan_wall_messages.find_one(
        {"id": message_id, "is_approved": True}, {"_id": 0, "id": 1, "likes_count": 1}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")

    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    user_agent = request.headers.get("user-agent", "")[:160]
    voter_hash = sha256(f"{message_id}:{client_ip}:{user_agent}".encode()).hexdigest()
    try:
        await db.fan_wall_reactions.insert_one({
            "message_id": message_id,
            "voter_hash": voter_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except DuplicateKeyError:
        return {**existing, "already_liked": True}

    updated = await db.fan_wall_messages.find_one_and_update(
        {"id": message_id, "is_approved": True}, {"$inc": {"likes_count": 1}},
        return_document=True, projection={"_id": 0, "id": 1, "likes_count": 1},
    )
    if not updated:
        await db.fan_wall_reactions.delete_one({"message_id": message_id, "voter_hash": voter_hash})
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")
    return {**updated, "already_liked": False}


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
async def shutdown_db_client():
    client.close()