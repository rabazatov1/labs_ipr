# k8s (лаб. 5)

Команды из папки **`lab_5`**.

## База

```bash
docker build -t k8s-lab5-backend:1.0 backend
docker build -t k8s-lab5-frontend:1.0 frontend
kubectl apply -k k8s/
kubectl get pods,svc -n lab5-fastapi
```

UI: NodePort 30080 (у minikube часто `minikube service …` или `kubectl port-forward svc/frontend-service 8080:80 -n lab5-fastapi`).

Проверка API через фронт: `curl -s http://localhost:30080/api/info` (если порт с хоста не ходит — см. выше).

## GHCR

```bash
kubectl set image deployment/backend-deployment backend=REG-backend:latest -n lab5-fastapi
kubectl set image deployment/frontend-deployment frontend=REG-frontend:latest -n lab5-fastapi
```

## Зад. 2 — Ingress

```bash
helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx -n ingress-nginx --create-namespace
```

В `/etc/hosts`: `127.0.0.1 lab5.local`  
`kubectl apply -f k8s/ingress.yaml`

## Зад. 3 — Prometheus + метрики + Loki

Пересобрать backend (есть `/metrics`), потом:

```bash
kubectl rollout restart deployment/backend-deployment -n lab5-fastapi
kubectl apply -k k8s/observability/
```

Проверка: `kubectl port-forward -n lab5-fastapi svc/backend-service 8000:8000` → в другом окне `curl -s localhost:8000/metrics | head`.  
Prometheus: `kubectl port-forward -n lab5-fastapi svc/prometheus 9090:9090` → `curl -s "http://localhost:9090/api/v1/targets?state=active" | head -c 500`  
Логи: `kubectl logs -n lab5-fastapi -l app=promtail --tail=15` и `kubectl logs -n lab5-fastapi -l app=loki --tail=10`

## Зад. 4 — HPA + нагрузка

Нужен metrics-server (`kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` или `minikube addons enable metrics-server`).

```bash
kubectl apply -f k8s/hpa-backend.yaml
kubectl apply -f k8s/jobs/load-backend-hpa.yaml
kubectl get hpa -n lab5-fastapi -w
```

Удалить job: `kubectl delete job lab5-load-backend -n lab5-fastapi`

## Удалить всё

```bash
kubectl delete namespace lab5-fastapi
kubectl delete clusterrolebinding lab5-promtail
kubectl delete clusterrole lab5-promtail
```
