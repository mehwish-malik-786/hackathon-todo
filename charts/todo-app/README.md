# Todo App Helm Chart

Helm chart for deploying Todo Chatbot Application to Kubernetes.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.x
- Dapr runtime installed (`dapr init -k`)

## Installation

### Local Development (Minikube)

```bash
# Install with default values
helm install todo-app ./charts/todo-app \
  --namespace todo-dev \
  --create-namespace

# Or use values file
helm install todo-app ./charts/todo-app \
  --namespace todo-dev \
  -f values-dev.yaml
```

### Production (Azure AKS)

```bash
# Install with production values
helm install todo-app ./charts/todo-app \
  --namespace todo-dev \
  -f values-prod.yaml
```

## Configuration

See `values.yaml` for all configurable options.

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Backend replicas | 2 |
| `backend.image.repository` | Backend image | todo-backend |
| `backend.image.tag` | Backend image tag | latest |
| `frontend.replicaCount` | Frontend replicas | 2 |
| `frontend.ingress.enabled` | Enable ingress | true |
| `frontend.ingress.host` | Ingress host | todo.local |
| `kafka.enabled` | Install Kafka | true |
| `redis.enabled` | Install Redis | true |
| `dapr.enabled` | Enable Dapr sidecars | true |
| `monitoring.prometheus.enabled` | Install Prometheus | true |
| `monitoring.grafana.enabled` | Install Grafana | true |

## Upgrade

```bash
helm upgrade todo-app ./charts/todo-app \
  --namespace todo-dev \
  --set backend.replicaCount=3
```

## Uninstall

```bash
helm uninstall todo-app -n todo-dev
```

## Monitoring

After installation:

```bash
# Access Grafana
kubectl port-forward svc/grafana -n todo-dev 3000:80
# http://localhost:3000 (admin/admin123)

# Access Prometheus
kubectl port-forward svc/prometheus-server -n todo-dev 9090:80
# http://localhost:9090
```
