import os
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import psycopg
except ImportError:
    psycopg = None

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="lab6-fastapi-backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


def get_database_target() -> dict[str, str | int | bool]:
    database_url = get_database_url()

    if not database_url:
        return {"configured": False}

    parsed = urlparse(database_url)

    return {
        "configured": True,
        "scheme": parsed.scheme or "postgres",
        "host": parsed.hostname or "неизвестно",
        "port": parsed.port or 5432,
        "database": parsed.path.removeprefix("/") or "неизвестно",
        "username": parsed.username or "неизвестно",
    }


def check_database_connection() -> dict[str, str | bool]:
    database_url = get_database_url()

    if not database_url:
        return {"ok": False, "reason": "Переменная DATABASE_URL не настроена"}

    if psycopg is None:
        return {"ok": False, "reason": "Библиотека psycopg не установлена"}

    try:
        with psycopg.connect(database_url, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}

    return {"ok": True, "reason": "Подключение к базе данных доступно"}


@app.get("/health")
def health() -> dict[str, str]:
    database = get_database_target()
    return {
        "status": "работает",
        "service": "серверная часть",
        "database_configured": "да" if database.get("configured", False) else "нет",
        "time": utc_now(),
    }


@app.get("/health/db")
def database_health() -> dict[str, object]:
    database_check = check_database_connection()
    database_target = get_database_target()

    if not database_check["ok"]:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "ошибка",
                "service": "серверная часть",
                "database": database_target,
                "database_check": database_check,
                "time": utc_now(),
            },
        )

    return {
        "status": "работает",
        "service": "серверная часть",
        "database": database_target,
        "database_check": database_check,
        "time": utc_now(),
    }


@app.get("/api/info")
def info() -> dict[str, object]:
    database_target = get_database_target()
    database_check = check_database_connection()

    return {
        "service": "серверная часть",
        "framework": "FastAPI",
        "message": "Серверная часть лабораторной работы 6 запущена",
        "environment": os.getenv("APP_ENV", "разработка"),
        "version": os.getenv("APP_VERSION", "2.0.0"),
        "pod_name": os.getenv("HOSTNAME", socket.gethostname()),
        "secret_loaded": bool(os.getenv("DEMO_API_KEY")),
        "database": database_target,
        "database_check": database_check,
        "time": utc_now(),
    }
