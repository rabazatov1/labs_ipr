Скриншоты для отчёта: Target в Prometheus, дашборд в Grafana, Explore → Tempo с trace. Имена файлов на усмотрение (например `prometheus-targets.png`, `grafana-dashboard.png`, `tempo-trace.png`).

Добавлено: `prometheus-targets.png` — страница Targets (оба job UP).

Добавлено: `prometheus-http-requests.png` — Graph/Table, запрос `http_requests_total` (серии по маршрутам).

Добавлено: `prometheus-diagnostic-reports-total.png` — запрос `diagnostic_reports_total` (бизнес-метрика).

Добавлено: `grafana-datasource-prometheus.png` — Connections → Data sources → Prometheus, успешный тест API.

Добавлено: `grafana-dashboard-lab7.png` — дашборд «Lab 7 — backend» (RPS, latency p95, diagnostic_reports_total).

Добавлено: `tempo-trace.png` — Explore → Tempo, TraceQL `{resource.service.name = "lab7-backend"}`, список трейсов.
