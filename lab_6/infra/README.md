# infra (лаб. 6)

`StatefulSet` postgres, headless `Service` (`clusterIP: None`), `volumeClaimTemplates` (PVC), `Secret` с учёткой. Развёртывание: Kustomize (base + dev/prod) и/или Helm-чарт `k8s/helm/postgres-infra`. Порядок и команды **из корня** `lab_6` — в **`app/k8s/README.md`**.

**Контракт** для `DATABASE_URL` (пароль в dev из values/Secret инфраструктуры):

| | Dev (один namespace с app) | Prod (БД в `lab6-data`, app в `lab6-prod`) |
|--|--|--|
| Хост | `postgres-0.postgres` | `postgres-0.postgres.lab6-data.svc.cluster.local` |
| Порт / БД / пользователь | `5432` / `lab6_app` / `lab6_user` | то же |

```text
postgres://lab6_user:PASSWORD@HOST:5432/lab6_app?sslmode=disable
```

Отсюда (из `infra/`, один раз для справки):

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

```bash
helm upgrade --install lab6-db ./k8s/helm/postgres-infra --namespace lab6-demo --create-namespace -f ./k8s/helm/postgres-infra/values-dev.yaml
```

Полный сценарий (включая `kubectl get storageclass` и `pvc`) — в `../app/k8s/README.md`.
