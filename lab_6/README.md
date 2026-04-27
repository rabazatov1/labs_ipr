# Лаб. 6 — Kustomize, Helm, инфра отдельно

PostgreSQL в `infra/`, backend и frontend в `app/`. В `app/k8s/` — только Kustomize и Helm чарта приложения, без манифестов БД. Подключение к БД через `DATABASE_URL` в Secret, у backend `GET /health` и `GET /health/db`. CI: `.github/workflows/lab6-ci.yml`, пуш в `main`/`master` — образы в GHCR.

Сборка: `app/backend`, `app/frontend`. Кластер, minikube, Kustomize, Helm — в **`app/k8s/README.md`**. Кратко про слой `infra` — в **`infra/README.md`**.

Порядок: сначала БД, потом приложение (подробности в `app/k8s/README.md`).
