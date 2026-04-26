from datetime import datetime, timezone
import os
import socket

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(title="lab5-fastapi-backend", version="1.0.0")

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "работает",
        "service": "серверная часть",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/info")
def info() -> dict[str, str | bool]:
    return {
        "service": "серверная часть",
        "framework": "FastAPI",
        "message": "Серверная часть лабораторной работы 5 запущена",
        "environment": os.getenv("APP_ENV", "разработка"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "pod_name": os.getenv("HOSTNAME", socket.gethostname()),
        "secret_loaded": bool(os.getenv("DEMO_API_KEY")),
        "time": datetime.now(timezone.utc).isoformat(),
    }
