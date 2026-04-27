# k8s (лаб. 7)

Команды из папки **`lab_7`**.

## Локально: Docker Compose (приложение + Prometheus + Grafana + Tempo)

```bash
cd app
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d
docker compose -f docker-compose.yml -f docker-compose.observability.yml ps
```

```bash
curl -sS http://localhost:8080/health
curl -sS http://localhost:8080/metrics
curl -sS http://localhost:8080/api/stats
```

Grafana `http://127.0.0.1:3001` (admin / admin), Prometheus **Targets:** `http://127.0.0.1:9090/targets` (только этот вариант compose).

Если `9090` не открывается: контейнеры не запущены (`docker compose ... ps`, должен быть сервис `prometheus`) или порт занят. Запуск обязательно **из `lab_7/app`**:  
`docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d` (два `-f`).

**Targets — backend DOWN / `no such host` / `connection refused`:** приложение и Prometheus в **одной** сети compose; в `app/observability/prometheus/prometheus.yml` target — **`lab7-backend:8000`** (внутренний порт, не `8080` с хоста). `host.docker.internal:8080` на Docker Desktop для macOS часто даёт `connection refused` — не используем. После смены конфига: `docker compose ... up -d --build --force-recreate`. Проверка:  
`docker compose -f docker-compose.yml -f docker-compose.observability.yml exec prometheus wget -qO- http://lab7-backend:8000/metrics | head`  
Конфиг в контейнере: `docker compose ... exec prometheus cat /etc/prometheus/prometheus.yml`

**Только** каталог `lab_7/observability` (без app в сети): Prometheus на хосте — **`http://127.0.0.1:19090/targets`**, не `9090`. Grafana `http://127.0.0.1:13001`.

## Minikube: образы

```bash
cd lab_7
eval "$(minikube docker-env)"
docker build -t lab7-backend:1.0.0 ./app/backend
docker build -t lab7-frontend:1.0.0 ./app/frontend
```

## Порядок: Postgres (лаб. 6) → observability (Tempo) → приложение (лаб. 7)

```bash
kubectl apply -k ../lab_6/infra/k8s/kustomization/overlays/dev
kubectl apply -k observability/k8s
kubectl apply -k app/k8s/kustomization/overlays/dev
```

(Если `lab_6` и `lab_7` рядом: из `lab_7` путь к инфе — `../lab_6/infra/...` при репо в `ИПР`.)

`Secret` `lab7-app-secret` ожидает PostgreSQL в `lab6-demo` (FQDN в `overlays/dev/secret.yaml`). `ServiceMonitor` требует CRD и Prometheus Operator (после `helm … kube-prometheus-stack`). Без operator удали `servicemonitor.yaml` из `kustomization.yaml` или не применяй кластер с отсутствующим `monitoring.coreos.com`.

## Проверка backend

```bash
kubectl get pods -n lab7-demo
kubectl port-forward -n lab7-demo svc/lab7-backend 8080:8000
```

```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8080/metrics
curl -sS http://127.0.0.1:8080/api/stats
```

Prometheus UI (после helm): `kubectl port-forward -n observability svc/prometheus-kube-prometheus-prometheus 9090:9090` — Targets: `lab7-backend`.

## Kustomize prod

```bash
kubectl apply -k ../lab_6/infra/k8s/kustomization/overlays/prod
kubectl apply -k observability/k8s
kubectl apply -k app/k8s/kustomization/overlays/prod
```

Секреты `prod` под реальные пароли.

## Helm

```bash
helm upgrade --install lab7-app ./app/k8s/helm/lab7-web-app \
  --namespace lab7-demo --create-namespace \
  -f ./app/k8s/helm/lab7-web-app/values-dev.yaml
```

NodePort в `values-dev`: **30806** (frontend), **30807** (backend). `imagePullPolicy: Never` — образы в minikube.

## Манифесты без кластера

```bash
kubectl kustomize app/k8s/kustomization/overlays/dev
helm template t ./app/k8s/helm/lab7-web-app -f ./app/k8s/helm/lab7-web-app/values-dev.yaml
```

## Удалить namespace

```bash
kubectl delete namespace lab7-demo
```
