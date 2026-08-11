import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
import turso_serverless


load_dotenv(Path(__file__).parent / ".env")
TURSO_DATABASE_URL = os.environ["TURSO_DATABASE_URL"]
TURSO_AUTH_TOKEN = os.environ["TURSO_AUTH_TOKEN"]


def connect_db():
    return turso_serverless.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)


def get_db() -> Generator:
    connection = connect_db()
    try:
        yield connection
    finally:
        connection.close()


def row_to_dict(cursor, row) -> dict:
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def rows_to_dicts(cursor) -> list[dict]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]