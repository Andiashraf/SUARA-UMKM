from datetime import datetime, timezone

from database import connect_db


MIGRATIONS = {
    1: [
        """CREATE TABLE IF NOT EXISTS fan_wall_messages (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            business_name TEXT NOT NULL,
            role TEXT NOT NULL,
            province TEXT NOT NULL,
            city_regency TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL,
            avatar_url TEXT NOT NULL DEFAULT '',
            avatar_path TEXT,
            likes_count INTEGER NOT NULL DEFAULT 0,
            is_approved INTEGER NOT NULL DEFAULT 0,
            is_featured INTEGER NOT NULL DEFAULT 0,
            moderation_status TEXT NOT NULL DEFAULT 'pending'
                CHECK (moderation_status IN ('pending','approved','rejected')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS fan_wall_reactions (
            id TEXT PRIMARY KEY,
            message_id TEXT NOT NULL REFERENCES fan_wall_messages(id) ON DELETE CASCADE,
            voter_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(message_id, voter_hash)
        )""",
        "CREATE INDEX IF NOT EXISTS ix_fan_wall_feed ON fan_wall_messages(moderation_status, is_featured, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS ix_fan_wall_role ON fan_wall_messages(role)",
        "CREATE INDEX IF NOT EXISTS ix_fan_wall_province ON fan_wall_messages(province)",
        "CREATE INDEX IF NOT EXISTS ix_fan_wall_likes ON fan_wall_messages(moderation_status, likes_count DESC)",
        "CREATE INDEX IF NOT EXISTS ix_fan_wall_reactions_message ON fan_wall_reactions(message_id)",
    ],
    2: [
        "ALTER TABLE fan_wall_messages ADD COLUMN instagram_url TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE fan_wall_messages ADD COLUMN linkedin_url TEXT NOT NULL DEFAULT ''",
    ]
}


def migrate_and_seed(seed_messages: list[dict]) -> None:
    connection = connect_db()
    try:
        connection.execute("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER NOT NULL)")
        if connection.execute("SELECT COUNT(*) FROM _schema_version").fetchone()[0] == 0:
            connection.execute("INSERT INTO _schema_version(version) VALUES (0)")
        current = connection.execute("SELECT version FROM _schema_version").fetchone()[0]
        for version in sorted(MIGRATIONS):
            if version > current:
                for statement in MIGRATIONS[version]:
                    connection.execute(statement)
                connection.execute("UPDATE _schema_version SET version = ?", (version,))
        now = datetime.now(timezone.utc).isoformat()
        for item in seed_messages:
            connection.execute(
                """INSERT OR IGNORE INTO fan_wall_messages (
                    id, full_name, business_name, role, province, city_regency, message,
                    avatar_url, avatar_path, likes_count, is_approved, is_featured,
                    moderation_status, instagram_url, linkedin_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item["id"], item["full_name"], item["business_name"], item["role"],
                    item["province"], item["city_regency"], item["message"], item["avatar_url"],
                    item.get("avatar_path"), item["likes_count"], 1, int(item["is_featured"]),
                    "approved", item.get("instagram_url", ""), item.get("linkedin_url", ""), now, now,
                ),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()