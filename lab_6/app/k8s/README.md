# k8s (лаб. 6)

Команды из папки **`lab_6`** (пути ниже с префиксом `app/` / `infra/`).

## Minikube: образы в Docker кластера

```bash
cd lab_6
eval "$(minikube docker-env)"
docker build -t lab6-backend:1.0.0 ./app/backend
docker build -t lab6-frontend:1.0.0 ./app/frontend
```

В dev: `imagePullPolicy: Never` (Kustomize + Helm `values-dev.yaml`), иначе kubelet тянет несуществующий образ с Docker Hub. Выход: `eval "$(minikube docker-env -u)"`.

## Предпосылки

```bash
kubectl get storageclass
```

## Kustomize — dev (namespace `lab6-demo`, БД и app вместе)

Сначала инфра, потом приложение:

```bash
kubectl apply -k infra/k8s/kustomization/overlays/dev
kubectl apply -k app/k8s/kustomization/overlays/dev
kubectl get pods,pvc,svc -n lab6-demo
```

NodePort Kustomize: фронт **30080**, бэк **30081** (доступ с хоста не везде; удобнее `port-forward`).

Проверка API (под `lab6-backend` в `Running`):

```bash
kubectl port-forward -n lab6-demo svc/lab6-backend 8080:8000
```

В другом окне:

```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8080/health/db
curl -sS http://127.0.0.1:8080/api/info
```

UI:

```bash
kubectl port-forward -n lab6-demo svc/lab6-frontend 8888:80
```

Альтернатива: `minikube service lab6-backend -n lab6-demo --url`.

## Kustomize — prod

Перед `apply`: проставить пароли в `infra/k8s/kustomization/overlays/prod/secret.yaml` и `app/k8s/kustomization/overlays/prod/secret.yaml` (и согласовать `database-url` в app с паролем postgres в `lab6-data`).

```bash
kubectl apply -k infra/k8s/kustomization/overlays/prod
kubectl apply -k app/k8s/kustomization/overlays/prod
```

## Helm (тот же dev, в `lab6-demo`)

Сначала БД, потом app:

```bash
helm upgrade --install lab6-db ./infra/k8s/helm/postgres-infra \
  --namespace lab6-demo --create-namespace \
  -f ./infra/k8s/helm/postgres-infra/values-dev.yaml
helm upgrade --install lab6-app ./app/k8s/helm/lab6-web-app \
  --namespace lab6-demo --create-namespace \
  -f ./app/k8s/helm/lab6-web-app/values-dev.yaml
```

NodePort **Helm** `values-dev`: бэк **30802**, фронт **30803** (не пересекаются с Kustomize **30081** / **30080**). Не вешать оба варианта на одну ноду с одинаковыми NodePort.

Отдельный namespace (нужен `--create-namespace` на оба `helm`):

```bash
helm upgrade --install lab6-db ./infra/k8s/helm/postgres-infra \
  --namespace lab6-helm-test --create-namespace \
  -f ./infra/k8s/helm/postgres-infra/values-dev.yaml
helm upgrade --install lab6-app ./app/k8s/helm/lab6-web-app \
  --namespace lab6-helm-test --create-namespace \
  -f ./app/k8s/helm/lab6-web-app/values-dev.yaml
```

`helm list -n <ns>`, `helm history`, `helm rollback <release> -n <ns>`, `helm uninstall <release> -n <ns>`.

## Сборка манифестов без кластера

```bash
kubectl kustomize infra/k8s/kustomization/overlays/dev
kubectl kustomize app/k8s/kustomization/overlays/dev
helm template t ./infra/k8s/helm/postgres-infra -f ./infra/k8s/helm/postgres-infra/values-dev.yaml
helm template t ./app/k8s/helm/lab6-web-app -f ./app/k8s/helm/lab6-web-app/values-dev.yaml
```

## GHCR (как в лаб. 5)

Имена смотри в выводе CI; подстановка в деплой:

```bash
kubectl set image deployment/lab6-backend backend=ghcr.io/OWNER/REPO-lab6-backend:latest -n lab6-demo
kubectl set image deployment/lab6-frontend frontend=ghcr.io/OWNER/REPO-lab6-frontend:latest -n lab6-demo
```

(при `imagePullSecrets`, если репозиторий приватный)

## Сбой: Pending / ImagePull

```bash
kubectl describe pod -n lab6-demo -l component=backend
kubectl get events -n lab6-demo --sort-by='.lastTimestamp' | tail -20
```

Нет образа в minikube — пересобрать с `minikube docker-env`, `kubectl rollout restart deployment/lab6-backend deployment/lab6-frontend -n lab6-demo`. Мало CPU/RAM — `minikube start --memory 4096 --cpus 2` или убрать чужие pod’ы (например `lab5`).

## Удалить dev-неймспейс

```bash
kubectl delete namespace lab6-demo
```

(и при проверке Helm) `lab6-helm-test` аналогично.
