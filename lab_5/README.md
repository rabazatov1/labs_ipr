# Лаб. 5 — Kubernetes + GitHub Actions

Backend на FastAPI, фронт на nginx+JS. В k8s nginx проксирует `/api` на backend (ClusterIP). CI: `.github/workflows/lab5-ci.yml`, образы в GHCR.

Структура: `backend/`, `frontend/`, `k8s/` (манифесты, см. `k8s/README.md`).

Локально: в `backend` — venv, `pip install -r requirements.txt`, `uvicorn app.main:app --host 0.0.0.0 --port 8000`. В `frontend/public` — `python3 -m http.server 3000`, в браузере порт 3000 (в `config.js` API на :8000).

Docker (из `lab_5`):  
`docker build -t k8s-lab5-backend:1.0 backend`  
`docker build -t k8s-lab5-frontend:1.0 frontend`

Кластер: `kubectl apply -k k8s/` — остальное в **`k8s/README.md`**.
