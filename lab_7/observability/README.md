# observability (лаб. 7)

Команды из папки **`lab_7/observability`** (или `cd lab_7/observability`).

## Только стек (порты как в курсе)

```bash
docker compose up -d
```

| Сервис    | URL |
|----------|-----|
| Prometheus | `http://localhost:19090` |
| Grafana  | `http://localhost:13001` (admin / admin) |
| Tempo UI | `http://localhost:13200` |
| OTLP HTTP | `http://localhost:14318` |

Backend на хосте: `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:14318`, `http://localhost:8080/metrics` — в scrape смотри `compose/prometheus/prometheus.yml` (`host.docker.internal:8080`).

## Kubernetes: Tempo

```bash
kubectl apply -k k8s
```

## Kubernetes: kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace observability --create-namespace \
  -f ./helm/kube-prometheus-stack/values-dev.yaml
```

Grafana: пароль `admin` по умолчанию. `ServiceMonitor` на backend — в `app/k8s/kustomization/overlays/`.

## Удалить

```bash
docker compose down
kubectl delete namespace observability
```
