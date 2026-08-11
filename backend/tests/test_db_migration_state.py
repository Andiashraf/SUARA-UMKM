"""Database migration and schema validation for Supabase PostgreSQL fan wall tables."""

import os
from pathlib import Path

import psycopg2
import pytest
from dotenv import load_dotenv


load_dotenv(Path("/app/backend/.env"))


@pytest.fixture(scope="session")
def database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is missing")
    return url


def test_alembic_head_revision_active(database_url):
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version_num FROM alembic_version")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "20260811_0001"


def test_fan_wall_tables_exist(database_url):
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN ('fan_wall_messages', 'fan_wall_reactions')
                """
            )
            names = {row[0] for row in cur.fetchall()}
            assert "fan_wall_messages" in names
            assert "fan_wall_reactions" in names
