import os
from pathlib import Path
import sqlite3
from typing import Generator

from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / ".env")


def connect_db():
    db_path = Path(__file__).parent / "app.db"
    return sqlite3.connect(db_path)


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