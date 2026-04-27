import os
from typing import Any

try:
    from prometheus_client import CONTENT_TYPE_LATEST
    from prometheus_client import Counter
    from prometheus_client import Histogram
    from prometheus_client import generate_latest
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    Counter = None
    Histogram = None
    generate_latest = None

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ImportError:
    trace = None
    OTLPSpanExporter = None
    FastAPIInstrumentor = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None


HTTP_REQUESTS_TOTAL = (
    Counter(
        "http_requests_total",
        "Общее количество HTTP-запросов",
        ("method", "route", "status"),
    )
    if Counter is not None
    else None
)

HTTP_REQUEST_DURATION_SECONDS = (
    Histogram(
        "http_request_duration_seconds",
        "Длительность HTTP-запросов в секундах",
        ("method", "route", "status"),
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
    )
    if Histogram is not None
    else None
)

DIAGNOSTIC_REPORTS_TOTAL = (
    Counter(
        "diagnostic_reports_total",
        "Количество сформированных диагностических отчётов приложения",
    )
    if Counter is not None
    else None
)

DATABASE_CHECKS_TOTAL = (
    Counter(
        "database_connection_checks_total",
        "Количество проверок доступности базы данных",
        ("result",),
    )
    if Counter is not None
    else None
)


def record_http_metrics(method: str, route: str, status_code: int, duration_seconds: float) -> None:
    if HTTP_REQUESTS_TOTAL is None or HTTP_REQUEST_DURATION_SECONDS is None:
        return

    status = str(status_code)
    HTTP_REQUESTS_TOTAL.labels(method=method, route=route, status=status).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=method,
        route=route,
        status=status,
    ).observe(duration_seconds)


def increment_diagnostic_reports() -> None:
    if DIAGNOSTIC_REPORTS_TOTAL is not None:
        DIAGNOSTIC_REPORTS_TOTAL.inc()


def record_database_check(ok: bool) -> None:
    if DATABASE_CHECKS_TOTAL is None:
        return

    DATABASE_CHECKS_TOTAL.labels(result="success" if ok else "error").inc()


def metrics_payload() -> tuple[bytes, str]:
    if generate_latest is None:
        return (
            b"# observability dependencies are not installed\n",
            CONTENT_TYPE_LATEST,
        )

    return generate_latest(), CONTENT_TYPE_LATEST


def init_tracing(app: Any) -> tuple[Any, str]:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    service_name = os.getenv("OTEL_SERVICE_NAME", "").strip() or "lab7-backend"

    if not endpoint:
        return None, "OTLP endpoint не задан, трейсинг отключён"

    if (
        trace is None
        or OTLPSpanExporter is None
        or FastAPIInstrumentor is None
        or Resource is None
        or TracerProvider is None
        or BatchSpanProcessor is None
    ):
        return None, "Пакеты OpenTelemetry не установлены"

    traces_endpoint = endpoint.rstrip("/")
    if not traces_endpoint.endswith("/v1/traces"):
        traces_endpoint = f"{traces_endpoint}/v1/traces"

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=traces_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    return provider, "Трейсинг включён"


def shutdown_tracing(app: Any, provider: Any) -> None:
    if provider is None:
        return

    if FastAPIInstrumentor is not None:
        FastAPIInstrumentor.uninstrument_app(app)

    provider.shutdown()


def get_tracer() -> Any:
    if trace is None:
        return None

    return trace.get_tracer("lab7-backend")
