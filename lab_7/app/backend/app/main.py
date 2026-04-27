import os
import socket
import time
from typing import Any
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import psycopg
except ImportError:
    psycopg = None

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware

from app.observability import get_tracer
from app.observability import increment_diagnostic_reports
from app.observability import init_tracing
from app.observability import metrics_payload
from app.observability import record_database_check
from app.observability import record_http_metrics
from app.observability import shutdown_tracing


SERVICE_LABEL = "серверная часть"
APP_VERSION = "3.0.0"
APP_TITLE = "lab7-fastapi-backend"

APP_STATS = {
    "diagnostic_reports_total": 0,
}

TRACING_STATUS = {
    "enabled": False,
    "message": "Трейсинг ещё не инициализирован",
}

_tracing_provider: Any = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        shutdown_tracing(app, _tracing_provider)


app = FastAPI(title=APP_TITLE, version=APP_VERSION, lifespan=lifespan)

_tracing_provider, _tracing_message = init_tracing(app)
TRACING_STATUS["enabled"] = _tracing_provider is not None
TRACING_STATUS["message"] = _tracing_message

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


def get_route_template(request: Request) -> str:
    route = request.scope.get("route")
    if route is None:
        return "unmatched"

    return getattr(route, "path", request.url.path)


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


def _check_database_connection(database_url: str) -> dict[str, str | bool]:
    if not database_url:
        record_database_check(False)
        return {"ok": False, "reason": "Переменная DATABASE_URL не настроена"}

    if psycopg is None:
        record_database_check(False)
        return {"ok": False, "reason": "Библиотека psycopg не установлена"}

    try:
        with psycopg.connect(database_url, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except Exception as exc:
        record_database_check(False)
        return {"ok": False, "reason": str(exc)}

    record_database_check(True)
    return {"ok": True, "reason": "Подключение к базе данных доступно"}


def check_database_connection() -> dict[str, str | bool]:
    database_url = get_database_url()
    tracer = get_tracer()

    if tracer is None:
        return _check_database_connection(database_url)

    with tracer.start_as_current_span("database.connection_check"):
        return _check_database_connection(database_url)


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next) -> Response:
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_seconds = time.perf_counter() - started_at
    record_http_metrics(
        method=request.method,
        route=get_route_template(request),
        status_code=response.status_code,
        duration_seconds=duration_seconds,
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    database = get_database_target()
    return {
        "status": "работает",
        "service": SERVICE_LABEL,
        "database_configured": "да" if database.get("configured", False) else "нет",
        "tracing_enabled": "да" if TRACING_STATUS["enabled"] else "нет",
        "time": utc_now(),
    }


@app.get("/metrics")
def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@app.get("/health/db")
def database_health() -> dict[str, object]:
    database_check = check_database_connection()
    database_target = get_database_target()

    if not database_check["ok"]:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "ошибка",
                "service": SERVICE_LABEL,
                "database": database_target,
                "database_check": database_check,
                "time": utc_now(),
            },
        )

    return {
        "status": "работает",
        "service": SERVICE_LABEL,
        "database": database_target,
        "database_check": database_check,
        "time": utc_now(),
    }


@app.get("/api/info")
def info() -> dict[str, object]:
    database_target = get_database_target()
    database_check = check_database_connection()

    return {
        "service": SERVICE_LABEL,
        "framework": "FastAPI",
        "message": "Серверная часть лабораторной работы 7 запущена",
        "environment": os.getenv("APP_ENV", "разработка"),
        "version": os.getenv("APP_VERSION", APP_VERSION),
        "pod_name": os.getenv("HOSTNAME", socket.gethostname()),
        "secret_loaded": bool(os.getenv("DEMO_API_KEY")),
        "database": database_target,
        "database_check": database_check,
        "tracing": TRACING_STATUS,
        "metrics_endpoint": "/metrics",
        "time": utc_now(),
    }


@app.get("/api/stats")
def stats() -> dict[str, object]:
    APP_STATS["diagnostic_reports_total"] += 1
    increment_diagnostic_reports()

    database_target = get_database_target()
    database_check = check_database_connection()

    return {
        "service": SERVICE_LABEL,
        "message": "Диагностический отчёт сформирован",
        "diagnostic_reports_total": APP_STATS["diagnostic_reports_total"],
        "database": database_target,
        "database_check": database_check,
        "tracing": TRACING_STATUS,
        "metrics_endpoint": "/metrics",
        "time": utc_now(),
    }
