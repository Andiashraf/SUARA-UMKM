from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from auth import authenticate_admin, require_admin
from database import get_db, row_to_dict, rows_to_dicts
from storage_service import remove_avatar


router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminLogin(BaseModel):
    email: str
    password: str


class ModerationUpdate(BaseModel):
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    is_featured: Optional[bool] = None


@router.post("/login")
def login(payload: AdminLogin, request: Request):
    token = authenticate_admin(payload.email, payload.password, request)
    return {"access_token": token, "token_type": "bearer", "expires_in": 1800, "email": payload.email.lower()}


@router.get("/me")
def admin_me(admin_email: str = Depends(require_admin)):
    return {"email": admin_email, "role": "Administrator"}


@router.get("/messages")
def list_admin_messages(
    status: str = Query(default="pending", pattern="^(pending|approved|rejected|all)$"),
    search: str = Query(default="", max_length=100),
    admin_email: str = Depends(require_admin),
    db=Depends(get_db),
):
    _ = admin_email
    conditions, params = [], []
    if status != "all":
        conditions.append("moderation_status = ?")
        params.append(status)
    if search.strip():
        conditions.append("(LOWER(full_name) LIKE LOWER(?) OR LOWER(business_name) LIKE LOWER(?) OR LOWER(message) LIKE LOWER(?))")
        pattern = f"%{search.strip()}%"
        params.extend([pattern, pattern, pattern])
    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    cursor = db.execute(f"SELECT * FROM fan_wall_messages{where} ORDER BY created_at DESC LIMIT 300", tuple(params))
    return rows_to_dicts(cursor)


@router.get("/stats")
def moderation_stats(admin_email: str = Depends(require_admin), db=Depends(get_db)):
    _ = admin_email
    pending, approved, rejected, featured = db.execute(
        """SELECT
            COALESCE(SUM(CASE WHEN moderation_status = 'pending' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN moderation_status = 'approved' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN moderation_status = 'rejected' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN is_featured = 1 THEN 1 ELSE 0 END), 0)
           FROM fan_wall_messages"""
    ).fetchone()
    return {"pending": pending, "approved": approved, "rejected": rejected, "featured": featured}


@router.patch("/messages/{message_id}")
def moderate_message(
    message_id: str,
    payload: ModerationUpdate,
    admin_email: str = Depends(require_admin),
    db=Depends(get_db),
):
    _ = admin_email
    cursor = db.execute("SELECT * FROM fan_wall_messages WHERE id = ?", (message_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")
    message = row_to_dict(cursor, row)
    status = payload.status or message["moderation_status"]
    featured = int(payload.is_featured) if payload.is_featured is not None else int(message["is_featured"])
    if status != "approved":
        featured = 0
    if featured and status != "approved":
        raise HTTPException(status_code=400, detail="Hanya aspirasi yang disetujui dapat dijadikan unggulan")
    db.execute(
        """UPDATE fan_wall_messages SET moderation_status = ?, is_approved = ?,
           is_featured = ?, updated_at = ? WHERE id = ?""",
        (status, int(status == "approved"), featured, datetime.now(timezone.utc).isoformat(), message_id),
    )
    db.commit()
    updated = db.execute("SELECT * FROM fan_wall_messages WHERE id = ?", (message_id,))
    return row_to_dict(updated, updated.fetchone())


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    admin_email: str = Depends(require_admin),
    db=Depends(get_db),
):
    _ = admin_email
    cursor = db.execute("SELECT avatar_path FROM fan_wall_messages WHERE id = ?", (message_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aspirasi tidak ditemukan")
    db.execute("DELETE FROM fan_wall_reactions WHERE message_id = ?", (message_id,))
    db.execute("DELETE FROM fan_wall_messages WHERE id = ?", (message_id,))
    db.commit()
    await remove_avatar(row[0])
    return {"ok": True, "id": message_id}