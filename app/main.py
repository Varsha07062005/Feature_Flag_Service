
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATABASE_PATH = Path(__file__).resolve().parent.parent / "feature_flags.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feature_flags (
                name TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 0
            )
        """)
    yield


app = FastAPI(
    title="Feature Flag Service",
    description="A simple API for managing feature flags.",
    version="1.0.0",
    lifespan=lifespan,
)


class FlagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    enabled: bool = False


class FlagUpdate(BaseModel):
    enabled: bool


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Feature Flag Service"}


@app.post("/flags", status_code=201)
def create_flag(flag: FlagCreate):
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO feature_flags (name, enabled) VALUES (?, ?)",
                (flag.name, int(flag.enabled)),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Feature flag already exists")

    return {"name": flag.name, "enabled": flag.enabled}


@app.get("/flags")
def list_flags():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT name, enabled FROM feature_flags ORDER BY name"
        ).fetchall()

    return [
        {"name": row["name"], "enabled": bool(row["enabled"])}
        for row in rows
    ]


@app.patch("/flags/{name}")
def update_flag(name: str, update: FlagUpdate):
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE feature_flags SET enabled = ? WHERE name = ?",
            (int(update.enabled), name),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Feature flag not found")

    return {"name": name, "enabled": update.enabled}


@app.get("/flags/{name}/evaluate")
def evaluate_flag(name: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT enabled FROM feature_flags WHERE name = ?",
            (name,),
        ).fetchone()

    return {"name": name, "enabled": bool(row["enabled"]) if row else False}
