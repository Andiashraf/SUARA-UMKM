"""One-time, idempotent transfer from the previous PostgreSQL database to Turso."""
from pathlib import Path
import os
import sys

import psycopg2
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from database import connect_db  # noqa: E402


MESSAGE_COLUMNS = [
    "id", "full_name", "business_name", "role", "province", "city_regency", "message",
    "avatar_url", "avatar_path", "likes_count", "is_approved", "is_featured",
    "moderation_status", "created_at", "updated_at",
]


def as_iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def migrate() -> dict:
    postgres = psycopg2.connect(os.environ["DATABASE_URL"])
    turso = connect_db()
    try:
        with postgres.cursor() as cursor:
            cursor.execute(f"SELECT {', '.join(MESSAGE_COLUMNS)} FROM fan_wall_messages")
            messages = cursor.fetchall()
            cursor.execute("SELECT id, message_id, voter_hash, created_at FROM fan_wall_reactions")
            reactions = cursor.fetchall()

        for row in messages:
            values = list(row)
            values[10] = int(values[10])
            values[11] = int(values[11])
            values[13] = as_iso(values[13])
            values[14] = as_iso(values[14])
            turso.execute(
                """INSERT INTO fan_wall_messages (
                    id, full_name, business_name, role, province, city_regency, message,
                    avatar_url, avatar_path, likes_count, is_approved, is_featured,
                    moderation_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    full_name=excluded.full_name, business_name=excluded.business_name,
                    role=excluded.role, province=excluded.province, city_regency=excluded.city_regency,
                    message=excluded.message, avatar_url=excluded.avatar_url,
                    avatar_path=excluded.avatar_path, likes_count=excluded.likes_count,
                    is_approved=excluded.is_approved, is_featured=excluded.is_featured,
                    moderation_status=excluded.moderation_status, updated_at=excluded.updated_at""",
                tuple(values),
            )
        for reaction in reactions:
            turso.execute(
                """INSERT OR IGNORE INTO fan_wall_reactions
                   (id, message_id, voter_hash, created_at) VALUES (?, ?, ?, ?)""",
                (reaction[0], reaction[1], reaction[2], as_iso(reaction[3])),
            )
        turso.commit()
        return {
            "source_messages": len(messages),
            "source_reactions": len(reactions),
            "target_messages": turso.execute("SELECT COUNT(*) FROM fan_wall_messages").fetchone()[0],
            "target_reactions": turso.execute("SELECT COUNT(*) FROM fan_wall_reactions").fetchone()[0],
        }
    except Exception:
        turso.rollback()
        raise
    finally:
        postgres.close()
        turso.close()


if __name__ == "__main__":
    print(migrate())