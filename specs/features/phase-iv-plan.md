# Phase IV: Local Kubernetes Architecture Plan

## Document Information

**Phase**: Phase IV (Local Kubernetes Deployment)  
**Version**: 1.0.0  
**Created**: 2026-03-12  
**Status**: Draft  
**Constitution**: `.specify/memory/phase-iv-v-constitution.md`  
**Specification**: `specs/features/phase-iv-local-kubernetes.md`

---

## Architecture Overview

### System Context Diagram

```mermaid
graph TB
    User[User/Browser] -->|HTTPS| Ingress[NGINX Ingress]
    Ingress --> Frontend[Frontend Service]
    Frontend -->|HTTP| Backend[Backend API Service]
    Backend -->|Dapr Invoke| DaprSidecar[Dapr Sidecar]
    DaprSidecar -->|Pub/Sub| Kafka[Kafka Cluster]
    DaprSidecar -->|State Store| Redis[Redis State Store]
    Kafka --> EventProcessor[Event Processor Service]
    EventProcessor -->|Dapr State| Redis
    subgraph Kubernetes Cluster [Minikube]
        Ingress
        Frontend
        Backend
        DaprSidecar
        Kafka
        Redis
        EventProcessor
    end
```

---

## Architecture Decisions

### ADR-001: Kafka Hosting Choice

**Decision**: Use **Bitnami Kafka Helm chart** for Phase IV (Minikube), **Confluent Cloud** for Phase V (Production)

**Rationale**:
- Bitnami: Lightweight, well-maintained, easy to install on Minikube
- Confluent Cloud: Managed service, reduces ops overhead in production
- Kafka-compatible APIs ensure no code changes between environments

**Alternatives Considered**:
- Redpanda: Lighter but less mature ecosystem
- Strimzi: More complex operator-based approach
- Self-managed: Too much ops overhead for Phase IV

---

### ADR-002: Dapr State Backend

**Decision**: Use **Redis** for Dapr state store (both Phase IV and V)

**Rationale**:
- Native Dapr support (first-class citizen)
- Fast in-memory operations with persistence options
- Simpler than PostgreSQL for key-value state
- Azure Cache for Redis / Memorystore available in production

**Alternatives Considered**:
- PostgreSQL: Better for complex queries but more complex setup
- MongoDB: Document store not needed for current use cases
- In-memory: Not suitable for production (data loss on restart)

---

### ADR-003: Monitoring Stack

**Decision**: Use **Prometheus + Grafana + Jaeger** (self-hosted for Phase IV, managed options for Phase V)

**Rationale**:
- CNCF standard tools
- Dapr has built-in Prometheus metrics
- OpenTelemetry integration for tracing
- Grafana dashboards easy to create and share

**Phase V Options**:
- Azure: Azure Monitor (managed Prometheus) + Grafana
- GCP: Cloud Monitoring + Grafana
- Multi-cloud: Grafana Cloud (managed)

---

### ADR-004: Logging Solution

**Decision**: Use **Fluent Bit + Loki** for log aggregation

**Rationale**:
- Lightweight (Fluent Bit written in C)
- Loki integrates well with Grafana
- Lower cost than ELK stack
- Sufficient for Phase IV/V requirements

**Alternatives Considered**:
- ELK Stack: More powerful but heavier resource usage
- Managed logging: Vendor lock-in concern
- stdout only: Not sufficient for production debugging

---

### ADR-005: Single-User Architecture

**Decision**: Start with **single-user** architecture (consistent with Phase I-III), design for multi-tenant future

**Rationale**:
- Maintains consistency with existing phases
- Simpler implementation
- Faster time to market
- Event schemas include `user_id` for future multi-tenant support

**Future Multi-Tenant Path**:
- Add `tenant_id` to event schemas
- Implement authentication layer
- Add user isolation at service level

---

## Service Boundaries

### Microservices Architecture

```mermaid
graph LR
    subgraph Frontend Tier
        FE[Frontend<br/>React SPA<br/>Port: 3000]
    end
    
    subgraph API Tier
        BE[Backend API<br/>FastAPI<br/>Port: 8000]
        DAPR[Dapr Sidecar<br/>gRPC/HTTP]
    end
    
    subgraph Event Processing Tier
        EP[Event Processor<br/>Kafka Consumer<br/>Port: 8004]
    end
    
    subgraph Data Tier
        KAFKA[(Kafka<br/>Event Bus)]
        REDIS[(Redis<br/>State Store)]
    end
    
    FE -->|HTTP/REST| BE
    BE -->|Dapr Invoke| DAPR
    DAPR -->|Pub/Sub| KAFKA
    DAPR -->|State API| REDIS
    KAFKA -->|Consume| EP
    EP -->|State API| REDIS
```

### Service Responsibility Matrix

| Service | Responsibility | Technology | Port | Dapr App ID |
|---------|---------------|------------|------|-------------|
| **Frontend** | UI, chat interface, task display | React + Nginx | 3000 | todo-frontend |
| **Backend API** | REST API, request validation, event publishing | FastAPI + Dapr SDK | 8000 | todo-backend |
| **Event Processor** | Event consumption, state persistence, projections | FastAPI + Dapr SDK | 8004 | todo-events |

### Service Communication Patterns

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend API
    participant D as Dapr Sidecar
    participant K as Kafka
    participant E as Event Processor
    participant R as Redis
    
    U->>F: Create Task (HTTP)
    F->>B: POST /tasks (JSON)
    B->>D: Publish Event (Dapr API)
    D->>K: task.created (Pub/Sub)
    B-->>F: 202 Accepted
    F-->>U: Task Created
    
    Note over K,E: Async Processing
    K->>E: Consume task.created
    E->>D: Save State (Dapr State API)
    D->>R: SET task:1 {data}
    E->>K: Publish task.persisted
```

---

## Scaling Strategy

### Horizontal Pod Autoscaler (HPA) Configuration

```mermaid
graph TB
    subgraph HPA Controller
        HPA[HPA Controller<br/>Metrics Server]
    end
    
    subgraph Frontend HPA
        FE1[Frontend Pod 1]
        FE2[Frontend Pod 2]
        FE3[Frontend Pod 3-N]
    end
    
    subgraph Backend HPA
        BE1[Backend Pod 1]
        BE2[Backend Pod 2]
        BE3[Backend Pod 3-N]
    end
    
    subgraph Event Processor HPA
        EP1[Event Pod 1]
        EP2[Event Pod 2]
        EP3[Event Pod 3-N]
    end
    
    HPA -->|Scale| FE1
    HPA -->|Scale| FE2
    HPA -->|Scale| FE3
    HPA -->|Scale| BE1
    HPA -->|Scale| BE2
    HPA -->|Scale| BE3
    HPA -->|Scale| EP1
    HPA -->|Scale| EP2
    HPA -->|Scale| EP3
    
    style FE3 fill:#f9f,stroke:#333,stroke-dasharray: 5 5
    style BE3 fill:#f9f,stroke:#333,stroke-dasharray: 5 5
    style EP3 fill:#f9f,stroke:#333,stroke-dasharray: 5 5
```

### Scaling Configuration Table

| Service | Min Replicas | Max Replicas | CPU Target | Memory Target | Scale-Up Cooldown | Scale-Down Cooldown |
|---------|-------------|--------------|------------|---------------|-------------------|---------------------|
| Frontend | 2 | 4 | 70% | 80% | 60s | 300s |
| Backend API | 2 | 10 | 70% | 80% | 60s | 300s |
| Event Processor | 2 | 6 | 70% | 80% | 60s | 300s |

### Scaling Triggers

```yaml
# Example HPA manifest
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
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

---

## Event Flow Architecture

### Event Publishing Flow

```mermaid
graph LR
    subgraph Backend Service
        B[Backend API]
        D[Dapr SDK]
    end
    
    subgraph Dapr Sidecar
        DS[Dapr Pub/Sub API]
    end
    
    subgraph Kafka
        K1[Topic: todo.tasks]
        K2[Topic: todo.chat]
        K3[Topic: todo.dead-letter]
    end
    
    B -->|1. Publish Event| D
    D -->|2. HTTP POST /v1.0/publish| DS
    DS -->|3. Route to topic| K1
    DS -->|4. On failure| K3
    
    style K3 fill:#fbb,stroke:#f33
```

### Event Consumption Flow

```mermaid
graph LR
    subgraph Kafka
        K[Kafka Topic]
    end
    
    subgraph Event Processor
        C[Consumer Group]
        H[Event Handler]
        P[Processor Logic]
    end
    
    subgraph Dapr Sidecar
        DS[Dapr State API]
    end
    
    subgraph Redis
        R[(Redis State Store)]
    end
    
    K -->|1. Poll events| C
    C -->|2. Deserialize| H
    H -->|3. Process| P
    P -->|4. Save State| DS
    DS -->|5. SET key| R
    
    style R fill:#bbf,stroke:#33f
```

### Event Topics and Partitions

| Topic | Partitions | Replication Factor | Retention | Consumer Groups |
|-------|-----------|-------------------|-----------|-----------------|
| `todo.tasks` | 3 | 1 | 7 days | event-processor-group |
| `todo.chat` | 3 | 1 | 7 days | chat-processor-group |
| `todo.dead-letter` | 1 | 1 | 30 days | dlq-monitor-group |

### Event Schema (CloudEvents 1.0)

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/todo-backend",
  "id": "uuid-v4",
  "time": "2026-03-12T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "task:1",
  "partitionkey": "user-123",
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

---

## Failover Handling

### Pod Failure Recovery

```mermaid
stateDiagram-v2
    [*] --> Running: Pod starts
    Running --> Failed: Container crash
    Running --> Terminated: OOMKilled
    Running --> Evicted: Node pressure
    
    Failed --> Restarting: RestartPolicy=Always
    Terminated --> Restarting: RestartPolicy=Always
    Evicted --> Pending: Scheduler finds new node
    
    Restarting --> Running: Container restarts
    Pending --> Running: Pod scheduled on new node
    
    Running --> [*]: Graceful shutdown
```

### Kafka Consumer Failover

```mermaid
graph TB
    subgraph Consumer Group [event-processor-group]
        C1[Consumer 1<br/>Partition 0]
        C2[Consumer 2<br/>Partition 1, 2]
    end
    
    subgraph Kafka Cluster
        P0[Partition 0]
        P1[Partition 1]
        P2[Partition 2]
    end
    
    P0 --> C1
    P1 --> C2
    P2 --> C2
    
    C2 -.->|Consumer fails| C1
    C1 -.->|Rebalance| P1
    C1 -.->|Rebalance| P2
    
    style C1 fill:#9f9,stroke:#393
```

### Failover Strategies

| Failure Type | Detection | Recovery Strategy | RTO | RPO |
|-------------|-----------|-------------------|-----|-----|
| Pod crash | Kubernetes liveness probe | Automatic restart (RestartPolicy=Always) | <30s | 0 |
| Node failure | Node not ready | Pod rescheduled on different node | <2min | 0 |
| Kafka broker failure | Connection timeout | Retry with backoff, failover to replica | <1min | <1min |
| Redis failure | Connection timeout | Retry, circuit breaker opens | <30s | 0 |
| Dapr sidecar failure | Health check fails | Sidecar restarts with pod | <30s | 0 |

### Circuit Breaker Pattern

```mermaid
stateDiagram-v2
    [*] --> Closed: Normal operation
    Closed --> Open: Failure threshold exceeded
    Open --> HalfOpen: Timeout elapsed
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure
    
    Closed --> Closed: Request succeeds
    Open --> Open: Request fails fast
```

---

## Kubernetes Services and Ingress

### Service Architecture

```mermaid
graph TB
    subgraph External
        User[User]
    end
    
    subgraph Ingress Layer
        Ing[NGINX Ingress Controller]
    end
    
    subgraph Services
        FrontendSvc[Frontend Service<br/>ClusterIP:3000]
        BackendSvc[Backend API Service<br/>ClusterIP:8000]
    end
    
    subgraph Pods
        FE1[Frontend Pod 1]
        FE2[Frontend Pod 2]
        BE1[Backend Pod 1]
        BE2[Backend Pod 2]
    end
    
    User --> Ing
    Ing --> FrontendSvc
    FrontendSvc --> FE1
    FrontendSvc --> FE2
    FE1 --> BackendSvc
    FE2 --> BackendSvc
    BackendSvc --> BE1
    BackendSvc --> BE2
```

### Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: todo.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
```

### Service Types

| Service Name | Type | Port | Target Port | Selector |
|-------------|------|------|-------------|----------|
| todo-frontend | ClusterIP | 80 | 3000 | app=todo-frontend |
| todo-backend | ClusterIP | 8000 | 8000 | app=todo-backend |
| kafka-headless | Headless | 9092 | 9092 | app=kafka |
| redis-master | ClusterIP | 6379 | 6379 | app=redis,role=master |

---

## Secrets Management

### Secrets Architecture

```mermaid
graph TB
    subgraph Kubernetes
        KS[Kubernetes Secrets]
    end
    
    subgraph Dapr
        DS[Dapr Secret Store Component]
    end
    
    subgraph Services
        BE[Backend Service]
        EP[Event Processor]
    end
    
    subgraph External Secrets
        RedisPwd[Redis Password]
        KafkaCreds[Kafka Credentials]
        JWTKey[JWT Secret Key]
    end
    
    External Secrets --> KS
    KS --> DS
    DS -->|Dapr Secret API| BE
    DS -->|Dapr Secret API| EP
```

### Secret Types and Storage

| Secret Name | Keys | Storage | Access Method |
|-------------|------|---------|---------------|
| redis-secret | password | Kubernetes Secret | Dapr Secret Store |
| kafka-secret | username, password | Kubernetes Secret | Dapr Secret Store |
| jwt-secret | key | Kubernetes Secret | Environment Variable (non-sensitive hash) |
| tls-secret | tls.crt, tls.key | Kubernetes Secret | Ingress TLS |

### Dapr Secret Store Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  auth:
    secret:
      name: k8s-secret
```

### Application Access Pattern

```python
# Backend service retrieves secret via Dapr
from dapr.clients import DaprClient

with DaprClient() as client:
    secret = client.get_secret(
        store_name='kubernetes-secrets',
        key='redis-password'
    )
    redis_password = secret.secret
```

---

## CI/CD Flow

### Pipeline Architecture

```mermaid
graph LR
    Dev[Developer] -->|git push| GitHub[GitHub Repository]
    GitHub -->|trigger| Actions[GitHub Actions]
    
    subgraph CI Pipeline
        Actions --> Test[Run Tests]
        Test --> Build[Build Docker Images]
        Build --> Scan[Security Scan - Trivy]
        Scan --> Push[Push to Registry]
    end
    
    subgraph CD Pipeline
        Push --> DeployDev[Deploy to Dev]
        DeployDev --> HealthDev[Health Checks]
        HealthDev --> DeployStaging[Deploy to Staging]
        DeployStaging --> IntegrationTest[Integration Tests]
        IntegrationTest --> Approve{Manual Approval}
        Approve -->|Approved| DeployProd[Deploy to Production]
    end
    
    DeployProd --> Notify[Slack Notification]
```

### GitHub Actions Workflow Structure

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    # Unit tests, integration tests
    steps: [checkout, setup-python, install-deps, run-tests]
  
  build:
    needs: test
    steps: [checkout, build-images, push-to-registry]
  
  security-scan:
    needs: build
    steps: [trivy-scan, upload-sarif]
  
  deploy-dev:
    needs: [build, security-scan]
    if: github.ref == 'refs/heads/develop'
    steps: [setup-minikube, install-dapr, helm-deploy, health-check]
  
  deploy-staging:
    needs: deploy-dev
    if: github.ref == 'refs/heads/main'
    steps: [helm-deploy-staging, integration-tests]
  
  deploy-prod:
    needs: deploy-staging
    environment: production
    steps: [helm-deploy-prod, smoke-tests, slack-notify]
```

### Deployment Strategy

```mermaid
graph TB
    subgraph Development
        DevMain[main branch]
        DevDeploy[Auto-deploy on merge]
    end
    
    subgraph Staging
        StageEnv[Staging Environment]
        StageTest[Integration Tests]
    end
    
    subgraph Production
        ProdEnv[Production Environment]
        Approval[Manual Approval]
    end
    
    DevMain --> DevDeploy
    DevDeploy --> StageEnv
    StageEnv --> StageTest
    StageTest --> Approval
    Approval --> ProdEnv
```

---

## Helm Charts Structure

### Chart Directory Layout

```
charts/
└── todo-app/
    ├── Chart.yaml                  # Chart metadata (version, app version, dependencies)
    ├── values.yaml                 # Default configuration values
    ├── values-dev.yaml             # Development environment overrides
    ├── values-staging.yaml         # Staging environment overrides
    ├── values-prod.yaml            # Production environment overrides
    ├── charts/                     # Subcharts (if any)
    └── templates/
        ├── _helpers.tpl            # Template helper functions
        ├── NOTES.txt               # Post-install notes
        ├── namespace.yaml          # Namespace definition
        ├── dapr-components/
        │   ├── pubsub-kafka.yaml   # Dapr pub/sub component
        │   ├── state-redis.yaml    # Dapr state store component
        │   └── secret-k8s.yaml     # Dapr secret store component
        ├── services/
        │   ├── frontend/
        │   │   ├── deployment.yaml
        │   │   ├── service.yaml
        │   │   ├── hpa.yaml
        │   │   ├── configmap.yaml
        │   │   ├── probes.yaml
        │   │   └── networkpolicy.yaml
        │   ├── backend/
        │   │   ├── deployment.yaml
        │   │   ├── service.yaml
        │   │   ├── hpa.yaml
        │   │   ├── configmap.yaml
        │   │   ├── probes.yaml
        │   │   └── networkpolicy.yaml
        │   └── event-processor/
        │       ├── deployment.yaml
        │       ├── service.yaml
        │       ├── hpa.yaml
        │       └── configmap.yaml
        ├── infrastructure/
        │   ├── ingress.yaml
        │   ├── networkpolicies.yaml
        │   └── rbac.yaml
        └── observability/
            ├── prometheus-servicemonitor.yaml
            ├── grafana-dashboards-configmap.yaml
            └── jaeger.yaml
```

### Chart Dependencies

```yaml
# Chart.yaml
apiVersion: v2
name: todo-app
description: Cloud-Native Todo Chatbot Application
type: application
version: 1.0.0
appVersion: "4.0.0"

dependencies:
- name: kafka
  version: 22.1.0
  repository: https://charts.bitnami.com/bitnami
  condition: kafka.enabled
- name: redis
  version: 18.0.0
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
- name: dapr
  version: 1.12.0
  repository: https://dapr.github.io/helm-charts/
  condition: dapr.enabled
```

---

## Migration Strategy from Minikube to AKS/GKE

### Migration Phases

```mermaid
graph LR
    subgraph Phase 1 [Preparation]
        P1[Create Cloud Infrastructure]
        P2[Configure Helm Values]
        P3[Setup CI/CD]
    end
    
    subgraph Phase 2 [Parallel Run]
        P4[Deploy to Cloud]
        P5[Run Smoke Tests]
        P6[Sync Data]
    end
    
    subgraph Phase 3 [Cutover]
        P7[Update DNS]
        P8[Switch Traffic]
        P9[Monitor]
    end
    
    subgraph Phase 4 [Decommission]
        P10[Verify Cloud Stable]
        P11[Shutdown Minikube]
    end
    
    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P9 --> P10 --> P11
```

### Configuration Changes Matrix

| Component | Minikube | AKS | GKE |
|-----------|----------|-----|-----|
| **Ingress Class** | nginx | azure/application-gateway | gce |
| **State Store** | Redis Helm | Azure Cache for Redis | Memorystore |
| **Kafka** | Bitnami Helm | Confluent Cloud | Confluent Cloud |
| **Secret Store** | Kubernetes Secrets | Azure Key Vault | GCP Secret Manager |
| **Monitoring** | Prometheus Helm | Azure Monitor | Cloud Monitoring |
| **Logging** | Loki Helm | Azure Log Analytics | Cloud Logging |
| **Load Balancer** | MetalLB | Azure Load Balancer | GCP Load Balancer |

### Migration Checklist

```markdown
## Pre-Migration
- [ ] Terraform scripts for AKS/GKE cluster
- [ ] Cloud-specific Helm values files created
- [ ] CI/CD pipeline updated for cloud deployment
- [ ] DNS records identified for update
- [ ] Monitoring baselines established

## Migration Execution
- [ ] Deploy application to cloud Kubernetes
- [ ] Run smoke tests against cloud deployment
- [ ] Verify all health checks passing
- [ ] Update DNS TTL to minimum (5 min)
- [ ] Switch DNS to cloud ingress IP
- [ ] Monitor error rates and latency

## Post-Migration
- [ ] Verify 100% traffic on cloud
- [ ] Monitor for 24 hours
- [ ] Update documentation
- [ ] Schedule Minikube decommission
```

### Rollback Strategy

```mermaid
graph TB
    Start[Migration Issue Detected] --> Check{Severity?}
    Check -->|Critical| ImmediateRollback[Immediate DNS Rollback]
    Check -->|Major| GradualRollback[Gradual Traffic Shift Back]
    Check -->|Minor| FixInCloud[Fix in Cloud, No Rollback]
    
    ImmediateRollback --> UpdateDNS[Update DNS to Minikube]
    UpdateDNS --> Verify[Verify Traffic Shifted]
    Verify --> Investigate[Investigate Root Cause]
    
    GradualRollback --> Shift25[25% Traffic to Minikube]
    Shift25 --> Monitor1[Monitor 5 min]
    Monitor1 --> Shift50[50% Traffic to Minikube]
    Shift50 --> Monitor2[Monitor 5 min]
    Monitor2 --> Shift100[100% Traffic to Minikube]
```

---

## Acceptance Criteria

### Architecture Validation

- [ ] All services have clear boundaries and responsibilities
- [ ] HPA configured for all services with appropriate thresholds
- [ ] Event flow documented with CloudEvents schema
- [ ] Failover handling tested for all failure scenarios
- [ ] Migration strategy documented and tested

### Technical Validation

- [ ] Helm chart passes lint validation
- [ ] Kubernetes manifests pass kubeval/kubeconform
- [ ] Dapr components properly configured
- [ ] Secrets management follows security best practices
- [ ] CI/CD pipeline executes successfully

### Operational Validation

- [ ] Monitoring dashboards created and accessible
- [ ] Alert rules configured and tested
- [ ] Runbooks documented for common scenarios
- [ ] Team trained on new architecture

---

**Version**: 1.0.0  
**Created**: 2026-03-12  
**Next**: Implementation Tasks (`phase-iv-tasks.md`)
