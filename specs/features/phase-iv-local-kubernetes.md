# Phase IV: Local Kubernetes Deployment Specification

## Feature Overview

**Feature Name**: Phase IV - Local Kubernetes Deployment  
**Phase**: Phase IV (Cloud-Native Foundation)  
**Priority**: P0 (Core Infrastructure)  
**Status**: Draft  
**Constitution**: `.specify/memory/phase-iv-v-constitution.md`

---

## Executive Summary

Phase IV containerizes the Todo Chatbot application and deploys it on a local Kubernetes cluster using Helm charts, Dapr service mesh, and Kafka event streaming. This establishes the cloud-native foundation required for Phase V cloud migration.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-IV-001 | Docker Containerization | P0 | Frontend and backend must be containerized with multi-stage builds |
| FR-IV-002 | Minikube Setup | P0 | Local Kubernetes cluster via Minikube with sufficient resources |
| FR-IV-003 | Helm Deployment | P0 | All services deployed via Helm charts with environment overrides |
| FR-IV-004 | Dapr Sidecar Integration | P0 | Dapr sidecars injected for pub/sub, state, service invocation |
| FR-IV-005 | Kafka Pub/Sub | P0 | Event-driven communication via Kafka message broker |
| FR-IV-006 | kubectl-ai/kagent | P1 | AI-powered cluster operations and debugging |
| FR-IV-007 | Health Checks | P0 | Liveness, readiness, startup probes for all services |
| FR-IV-008 | Replica Scaling | P0 | HPA-based horizontal scaling (2-10 replicas per service) |
| FR-IV-009 | GitHub Actions CI/CD | P0 | Automated build, test, deploy pipeline |
| FR-IV-010 | Observability | P0 | Prometheus metrics, Grafana dashboards, Jaeger tracing |

### Non-Functional Requirements

| ID | Requirement | Target | Description |
|----|-------------|--------|-------------|
| NFR-IV-001 | Availability | 99.5% | Local deployment uptime |
| NFR-IV-002 | Latency | <500ms | Inter-service communication via Dapr |
| NFR-IV-003 | Resource Usage | <3GB RAM | Total Minikube cluster memory |
| NFR-IV-004 | Image Size | <250MB | Per Docker image (alpine base) |
| NFR-IV-005 | Startup Time | <60s | Full application startup |
| NFR-IV-006 | Recovery Time | <30s | Pod restart and recovery |
| NFR-IV-007 | CI/CD Duration | <10 min | Pipeline execution time |

---

## User Journeys

### Journey 1: Developer Local Setup

```
User Story: As a developer, I want to deploy the app locally on Kubernetes
            so I can test cloud-native features before production.

Steps:
1. Install Minikube, Helm, kubectl, Dapr CLI
2. Start Minikube: minikube start --cpus=4 --memory=4096
3. Enable ingress: minikube addons enable ingress
4. Install Dapr: dapr init -k
5. Install Kafka: helm install kafka bitnami/kafka
6. Deploy app: helm install todo-app ./charts/todo-app -f values-dev.yaml
7. Access app: http://todo-app.local
8. Monitor: kubectl-ai get pods --explain

Expected Outcome:
- All pods running with Dapr sidecars
- Ingress accessible via localhost
- Health checks passing
- Metrics visible in Grafana
```

### Journey 2: Automated Deployment

```
User Story: As a developer, I want CI/CD to automatically deploy my changes
            so I can focus on coding without manual deployment steps.

Steps:
1. Developer pushes code to GitHub
2. GitHub Actions pipeline triggers
3. Tests run (unit + integration)
4. Docker images built and scanned (Trivy)
5. Images pushed to container registry
6. Helm chart packaged and published
7. Deployment to Minikube (or cloud in Phase V)
8. Health checks validate deployment
9. Notification sent (Slack/Email)

Expected Outcome:
- Zero-downtime deployment
- Rollback on failure
- Deployment report in PR
```

### Journey 3: Event-Driven Task Creation

```
User Story: As a user, I want to create tasks via chat
            so the system processes them asynchronously and reliably.

Steps:
1. User sends: "Add task buy milk tomorrow"
2. Frontend → Backend API (HTTP)
3. Backend → Dapr Pub/Sub (event: task.created)
4. Dapr → Kafka topic: todo.tasks
5. Event Processor consumes event
6. Event Processor → Dapr State Store (persist task)
7. Event Processor → Kafka topic: todo.task.persisted
8. Query Service updates projection
9. Response sent to user: "✅ Task created"

Expected Outcome:
- Task created asynchronously
- Event persisted in Kafka
- System decoupled and scalable
- User receives confirmation
```

### Journey 4: Scaling Under Load

```
User Story: As a platform engineer, I want services to scale automatically
            so the system handles load spikes without manual intervention.

Steps:
1. Load increases (100 concurrent users)
2. HPA detects CPU > 70% on backend-api
3. HPA scales backend-api from 2 → 5 replicas
4. New pods start with Dapr sidecars
5. Load balancer distributes traffic
6. Kafka handles increased event volume
7. Load decreases
8. HPA scales down to 2 replicas

Expected Outcome:
- Automatic scaling without downtime
- Resource optimization
- Cost efficiency
- Performance maintained under load
```

---

## Technical Specifications

### Containerization Strategy

#### Frontend Dockerfile (Multi-Stage)
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Backend Dockerfile (Multi-Stage)
```dockerfile
# Build stage
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Minikube Setup

```bash
# Create cluster with sufficient resources
minikube start \
  --cpus=4 \
  --memory=4096 \
  --disk-size=20gb \
  --driver=docker \
  --kubernetes-version=stable

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Install Dapr
dapr init -k --wait

# Verify Dapr
kubectl get pods -n dapr-system
```

### Helm Chart Structure

```
charts/
└── todo-app/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    ├── values-staging.yaml
    └── templates/
        ├── _helpers.tpl
        ├── namespace.yaml
        ├── dapr-components/
        │   ├── pubsub-kafka.yaml
        │   ├── state-redis.yaml
        │   └── secret-kubernetes.yaml
        ├── services/
        │   ├── frontend/
        │   │   ├── deployment.yaml
        │   │   ├── service.yaml
        │   │   ├── hpa.yaml
        │   │   ├── configmap.yaml
        │   │   └── probes.yaml
        │   └── backend/
        │       ├── deployment.yaml
        │       ├── service.yaml
        │       ├── hpa.yaml
        │       ├── configmap.yaml
        │       └── probes.yaml
        ├── infrastructure/
        │   ├── ingress.yaml
        │   ├── networkpolicies.yaml
        │   └── rbac.yaml
        └── observability/
            ├── prometheus-servicemonitor.yaml
            ├── grafana-dashboards-configmap.yaml
            └── jaeger.yaml
```

### Dapr Sidecar Configuration

#### Deployment Annotation Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "appconfig"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
```

### Kafka Pub/Sub Setup

#### Kafka Installation (Bitnami Helm)
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set persistence.size=10Gi \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=512Mi \
  --namespace todo-infra
```

#### Dapr Pub/Sub Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-dev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-0.kafka-headless.todo-infra.svc.cluster.local:9092"
  - name: authType
    value: "none"
  - name: consumeRetryInterval
    value: "100ms"
```

### Kafka Topic Definitions

| Topic | Partitions | Replication | Retention | Purpose |
|-------|------------|-------------|-----------|---------|
| `todo.tasks` | 3 | 1 | 7 days | Task CRUD events |
| `todo.chat` | 3 | 1 | 7 days | Chat messages |
| `todo.reminders` | 3 | 1 | 7 days | Reminder events |
| `todo.dead-letter` | 1 | 1 | 30 days | Failed events |

### Event Schema Definitions

#### task.created Event (CloudEvents 1.0)
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "time": "2026-03-12T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "task:1",
  "data": {
    "task_id": 1,
    "title": "Buy milk",
    "description": "From grocery store",
    "status": "pending",
    "created_by": "user-123",
    "created_at": "2026-03-12T10:30:00Z"
  }
}
```

#### task.updated Event
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.updated",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "time": "2026-03-12T10:35:00Z",
  "datacontenttype": "application/json",
  "subject": "task:1",
  "data": {
    "task_id": 1,
    "title": "Buy almond milk",
    "description": "From grocery store",
    "status": "pending",
    "updated_by": "user-123",
    "updated_at": "2026-03-12T10:35:00Z",
    "changes": ["title"]
  }
}
```

#### task.completed Event
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.completed",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "time": "2026-03-12T11:00:00Z",
  "datacontenttype": "application/json",
  "subject": "task:1",
  "data": {
    "task_id": 1,
    "title": "Buy almond milk",
    "status": "completed",
    "completed_by": "user-123",
    "completed_at": "2026-03-12T11:00:00Z"
  }
}
```

#### chat.message Event
```json
{
  "specversion": "1.0",
  "type": "com.todo.chat.message",
  "source": "/todo-frontend",
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "time": "2026-03-12T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "session:user-123",
  "data": {
    "session_id": "user-123",
    "message": "Add task buy milk tomorrow",
    "user_id": "user-123",
    "timestamp": "2026-03-12T10:30:00Z"
  }
}
```

### Health Checks Configuration

#### Backend Probes
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health/startup
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 12
```

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
  namespace: todo-dev
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

### kubectl-ai and kagent Usage

#### kubectl-ai Examples
```bash
# Explain pod issues
kubectl-ai get pod todo-backend-abc123 --explain

# Debug deployment
kubectl-ai debug deployment todo-backend

# Generate manifest
kubectl-ai generate deployment todo-backend --image=todo-backend:latest

# Analyze logs
kubectl-ai logs todo-backend-abc123 --analyze
```

#### kagent Examples
```bash
# Cluster health check
kagent cluster health

# Resource optimization
kagent optimize resources todo-dev

# Security audit
kagent audit security --namespace todo-dev

# Cost analysis
kagent cost analysis --namespace todo-dev
```

### GitHub Actions CI/CD Pipeline

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
    - uses: actions/checkout@v4
    
    - name: Generate version
      id: version
      run: echo "version=${{ github.sha }}" >> $GITHUB_OUTPUT
    
    - name: Build Docker images
      run: |
        docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ steps.version.outputs.version }} ./frontend
        docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ steps.version.outputs.version }} ./backend
    
    - name: Push to registry
      run: |
        echo ${{ secrets.GITHUB_TOKEN }} | docker login ${{ env.REGISTRY }} -u ${{ github.actor }} --password-stdin
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ steps.version.outputs.version }}
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ steps.version.outputs.version }}

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Trivy scan frontend
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ needs.build.outputs.version }}
        format: 'sarif'
        output: 'trivy-frontend.sarif'
    
    - name: Trivy scan backend
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ needs.build.outputs.version }}
        format: 'sarif'
        output: 'trivy-backend.sarif'
    
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-backend.sarif'

  deploy-dev:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Minikube
      uses: medyagh/setup-minikube@latest
      with:
        cpus: 4
        memory: 4096
    
    - name: Install Dapr
      run: dapr init -k --wait
    
    - name: Deploy with Helm
      run: |
        helm upgrade --install todo-app ./charts/todo-app \
          -f charts/todo-app/values-dev.yaml \
          --set image.tag=${{ needs.build.outputs.version }} \
          --namespace todo-dev \
          --create-namespace \
          --wait \
          --timeout 5m
    
    - name: Health check
      run: |
        kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-dev --timeout=120s
        kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-dev --timeout=120s

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        helm upgrade --install todo-app ./charts/todo-app \
          -f charts/todo-app/values-staging.yaml \
          --set image.tag=${{ needs.build.outputs.version }} \
          --namespace todo-staging \
          --create-namespace \
          --atomic \
          --timeout 10m
```

---

## Acceptance Criteria

### Phase IV Must Have (P0)

#### Containerization
- [ ] Frontend Dockerfile with multi-stage build (<250MB)
- [ ] Backend Dockerfile with multi-stage build (<250MB)
- [ ] Both images pass Trivy scan (zero critical vulnerabilities)
- [ ] Non-root user configured in containers
- [ ] Health check endpoints implemented

#### Minikube Setup
- [ ] Minikube cluster created with 4 CPU, 4GB RAM
- [ ] Ingress addon enabled
- [ ] Metrics server enabled
- [ ] Dapr runtime installed and verified

#### Helm Deployment
- [ ] Helm chart created with semantic versioning
- [ ] values.yaml with all configurable parameters
- [ ] values-dev.yaml for local development
- [ ] values-staging.yaml for staging environment
- [ ] Helm lint passes without errors
- [ ] Helm template renders valid Kubernetes manifests

#### Dapr Integration
- [ ] Dapr sidecars injected for all services
- [ ] Pub/sub component configured (Kafka)
- [ ] State store component configured (Redis)
- [ ] Service invocation working via Dapr API
- [ ] Dapr configuration applied (appconfig)

#### Kafka Setup
- [ ] Kafka broker running (Bitnami Helm chart)
- [ ] Topics created: todo.tasks, todo.chat, todo.reminders, todo.dead-letter
- [ ] Producer can publish events
- [ ] Consumer can subscribe and process events
- [ ] Dead letter queue handles failures

#### kubectl-ai/kagent
- [ ] kubectl-ai installed and configured
- [ ] kagent installed and configured
- [ ] Team trained on basic commands
- [ ] Debugging workflow documented

#### Health Checks
- [ ] Liveness probes configured for all services
- [ ] Readiness probes configured for all services
- [ ] Startup probes configured for all services
- [ ] Probes tested and passing

#### Replica Scaling
- [ ] HPA configured for frontend (min 2, max 4)
- [ ] HPA configured for backend (min 2, max 10)
- [ ] CPU target 70%, memory target 80%
- [ ] Scaling behavior tested under load
- [ ] Pod disruption budget configured

#### CI/CD Pipeline
- [ ] GitHub Actions workflow created
- [ ] Tests run on every push/PR
- [ ] Docker images built and pushed
- [ ] Security scanning integrated (Trivy)
- [ ] Helm chart published
- [ ] Auto-deploy to dev on merge
- [ ] Pipeline completes in <10 minutes

#### Observability
- [ ] Prometheus metrics exposed (/metrics)
- [ ] Grafana dashboards created (per service + overview)
- [ ] Jaeger tracing configured
- [ ] Logs aggregated (Fluent Bit + Loki)
- [ ] Alerting rules configured

---

## Testing Requirements

### Unit Tests
| Component | Coverage Target |
|-----------|-----------------|
| Backend API | 85% |
| Frontend Components | 80% |
| Event Handlers | 90% |

### Integration Tests
- [ ] Dapr pub/sub publish/subscribe
- [ ] Kafka event flow (end-to-end)
- [ ] Dapr state store operations
- [ ] Service-to-service invocation
- [ ] Health check endpoints

### Kubernetes Tests
- [ ] Helm chart lint
- [ ] Kubernetes manifest validation
- [ ] Resource limits enforcement
- [ ] HPA scaling simulation
- [ ] NetworkPolicy verification
- [ ] Pod disruption budget test

### Performance Tests
- [ ] Load test: 100 concurrent users
- [ ] Event throughput: >500 events/sec
- [ ] P95 latency: <500ms
- [ ] Recovery time: <30s after pod failure

---

## Security Requirements

### Image Security
- [ ] Alpine base images only
- [ ] Non-root user in all containers
- [ ] Read-only root filesystem
- [ ] Trivy scan: zero critical vulnerabilities
- [ ] Images signed (cosign)

### Network Security
- [ ] NetworkPolicies: deny-all default
- [ ] Explicit allow rules per service
- [ ] mTLS enabled via Dapr
- [ ] Ingress TLS termination

### Secrets Security
- [ ] Kubernetes Secrets for sensitive data
- [ ] RBAC restricts secret access
- [ ] No secrets in environment variables
- [ ] Secret rotation policy documented

---

## Observability Requirements

### Logging
- [ ] Structured JSON logs
- [ ] Correlation ID in all logs
- [ ] Log level configurable (INFO/DEBUG)
- [ ] Fluent Bit → Loki aggregation
- [ ] 30-day retention

### Metrics
- [ ] Prometheus endpoint (/metrics)
- [ ] Custom business metrics
- [ ] Service-level metrics (requests, errors, latency)
- [ ] Grafana dashboards deployed
- [ ] Alerting rules configured

### Tracing
- [ ] OpenTelemetry via Dapr
- [ ] W3C Trace Context propagation
- [ ] Jaeger UI accessible
- [ ] Trace sampling: 100% dev, 10% prod

---

## Resource Requirements

### Minikube Cluster
```bash
minikube start \
  --cpus=4 \
  --memory=4096 \
  --disk-size=20gb
```

### Service Resources

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 128Mi | 512Mi |
| Backend | 200m | 1000m | 256Mi | 1Gi |
| Kafka | 250m | 1000m | 512Mi | 2Gi |
| Redis | 100m | 500m | 128Mi | 512Mi |
| Dapr Sidecar | 50m | 200m | 64Mi | 256Mi |

**Total Estimated**: ~2.5GB RAM, ~3 CPU cores

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Minikube resource constraints | High | Medium | Optimize requests, use lightweight components |
| Dapr learning curve | Medium | High | Documentation, training, examples |
| Kafka complexity | Medium | Medium | Use single broker for dev, managed in prod |
| Helm chart errors | Medium | Low | Helm lint in CI, test deployments |
| Image vulnerabilities | High | Low | Trivy scan in CI, base image updates |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment Success Rate | 95% | Helm deploy success/failure |
| Service Availability | 99.5% | Uptime monitoring |
| Event Throughput | 500+ events/sec | Kafka metrics |
| P95 Latency | <500ms | Dapr invocation metrics |
| Mean Time to Recovery | <30s | Pod restart time |
| CI/CD Duration | <10 min | GitHub Actions runtime |
| Image Vulnerabilities | 0 critical | Trivy scan results |

---

## References

- **Constitution**: `.specify/memory/phase-iv-v-constitution.md`
- **Phase III Spec**: `specs/features/phase-iii-ai-chatbot.md`
- **Dapr Docs**: https://docs.dapr.io/
- **Kafka Docs**: https://kafka.apache.org/documentation/
- **Helm Docs**: https://helm.sh/docs/
- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/
- **kubectl-ai**: https://github.com/sozercan/kubectl-ai
- **kagent**: https://github.com/kagent/kagent

---

**Version**: 1.0.0  
**Created**: 2026-03-12  
**Author**: AI Assistant (Spec-Driven Development)  
**Status**: Draft - Awaiting User Approval  
**Next**: Architecture Plan (`phase-iv-plan.md`) → Implementation Tasks (`phase-iv-tasks.md`)
