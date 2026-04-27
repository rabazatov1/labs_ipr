# Лаб. 7 — Observability (Prometheus, Grafana, Tempo)

Backend FastAPI: `/metrics` (HTTP counter/histogram по шаблону маршрута, бизнес-метрика `diagnostic_reports_total`), опциональный OTLP в Tempo. Код в `app/`; стек Prometheus/Grafana/Tempo в `app/observability` (с приложением) и в `observability/` (только стек). В Kubernetes: `ServiceMonitor` в kustomize overlay, Tempo в `observability/k8s/`, `kube-prometheus-stack` в **lab_7/observability/helm** (см. `observability/README.md`). Сначала `lab_6/infra` (Postgres), затем `observability` и `app` — подробно в **`app/k8s/README.md`**. CI: `.github/workflows/lab7-ci.yml` → GHCR. Скриншоты к отчёту: `docs/screenshots/lab7/`.

Локально (Docker) — **два варианта портов**:

| Сценарий | Команда (из `lab_7`) | Prometheus (Targets) | Grafana | Backend `/metrics` |
|----------|----------------------|------------------------|---------|-------------------|
| Приложение + стек | `app/`: `docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d` | `http://127.0.0.1:9090/targets` | `http://127.0.0.1:3001` | `http://127.0.0.1:8080/metrics` |
| Только стек, без app в compose | `observability/`: `docker compose up -d` | `http://127.0.0.1:19090/targets` (не 9090) | `http://127.0.0.1:13001` | с хоста на 8080, scrape через `host.docker.internal` в конфиге |

Если `127.0.0.1:9090` не открывается — чаще всего не запущен compose из **`app/`** с обоими файлами, или занят другой процесс. Проверка: `docker ps` (сервис `prometheus` из проекта `lab7-app`) или `lsof -i :9090`. Подробно в **`app/k8s/README.md`**.
