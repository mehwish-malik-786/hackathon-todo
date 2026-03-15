# Phase IV: Implementation Tasks

## Document Information

**Phase**: Phase IV (Local Kubernetes Deployment)  
**Version**: 1.0.0  
**Created**: 2026-03-12  
**Status**: Ready for Implementation  
**Constitution**: `.specify/memory/phase-iv-v-constitution.md`  
**Specification**: `specs/features/phase-iv-local-kubernetes.md`  
**Architecture Plan**: `specs/features/phase-iv-plan.md`

---

## Task Summary

| Category | Task Count | Priority Breakdown |
|----------|-----------|-------------------|
| Infrastructure | 4 | P0: 4 |
| Containerization | 3 | P0: 3 |
| Dapr Components | 3 | P0: 3 |
| Kafka Setup | 2 | P0: 2 |
| Helm Charts | 5 | P0: 5 |
| Scaling | 2 | P0: 2 |
| Health Checks | 2 | P0: 2 |
| Observability | 3 | P0: 3 |
| CI/CD | 3 | P0: 3 |
| Security | 2 | P0: 2 |
| Testing | 3 | P0: 3 |
| Documentation | 1 | P1: 1 |
| **Total** | **33** | **P0: 32, P1: 1** |

---

## Infrastructure Tasks

### PH4-INF-001: Setup Minikube Cluster

**Task ID**: PH4-INF-001  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create and configure Minikube Kubernetes cluster with sufficient resources (4 CPU, 4GB RAM, 20GB disk) for Phase IV deployment.

**Preconditions**:
- Docker installed and running
- kubectl installed
- User has permissions to create Docker containers
- Minimum 8GB RAM available on host machine

**Expected Output**:
- Minikube cluster running with 4 CPUs, 4GB RAM, 20GB disk
- Kubernetes version 1.28+ accessible via kubectl
- Cluster status: Running (verified via `minikube status`)
- kubectl context set to minikube

**Files to Create**:
- None (infrastructure setup)

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Minikube Setup
- Section: Requirements → FR-IV-002

**Acceptance Criteria**:
- [ ] `minikube status` returns host: Running, kubelet: Running, apiserver: Running
- [ ] `kubectl cluster-info` shows Kubernetes control plane is running
- [ ] `kubectl get nodes` shows minikube node Ready
- [ ] `kubectl describe node minikube` shows CPU: 4, Memory: 4Gi

---

### PH4-INF-002: Enable Minikube Addons

**Task ID**: PH4-INF-002  
**Priority**: P0  
**Estimated Hours**: 1

**Description**: Enable required Minikube addons for ingress controller, metrics server, and storage provisioner.

**Preconditions**:
- PH4-INF-001 completed (Minikube cluster running)
- Minikube cluster accessible via kubectl

**Expected Output**:
- Ingress addon enabled and nginx-ingress-controller running
- Metrics-server addon enabled and running
- Storage-provisioner addon enabled
- All addon pods in Running state

**Files to Create**:
- None (addon configuration)

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Minikube Setup
- Section: Observability Requirements → Metrics

**Acceptance Criteria**:
- [ ] `minikube addons list` shows ingress: enabled, metrics-server: enabled
- [ ] `kubectl get pods -n ingress-nginx` shows nginx-ingress-controller-* Running
- [ ] `kubectl get pods -n kube-system` shows metrics-server-* Running

---

### PH4-INF-003: Install Dapr Runtime

**Task ID**: PH4-INF-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Install Dapr runtime on Kubernetes cluster using dapr CLI for microservices building blocks.

**Preconditions**:
- PH4-INF-001 completed (Minikube cluster running)
- Helm 3.x installed
- Internet access for downloading Dapr installer

**Expected Output**:
- Dapr CLI installed (version 1.12+)
- Dapr initialized on Kubernetes
- All Dapr system pods running in dapr-system namespace:
  - dapr-dashboard-*
  - dapr-operator-*
  - dapr-placement-server-*
  - dapr-sentry-*

**Files to Create**:
- None (runtime installation)

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-004 (Dapr Integration)
- Section: Technical Specifications → Dapr Sidecar Configuration

**Acceptance Criteria**:
- [ ] `dapr --version` shows CLI version 1.12.x
- [ ] `kubectl get pods -n dapr-system` shows all 4 Dapr pods Running
- [ ] `dapr components -k` executes without errors

---

### PH4-INF-004: Create Kubernetes Namespace

**Task ID**: PH4-INF-004  
**Priority**: P0  
**Estimated Hours**: 1

**Description**: Create dedicated Kubernetes namespace `todo-dev` with resource quotas and limit ranges for Phase IV application.

**Preconditions**:
- PH4-INF-001 completed (Minikube cluster running)
- kubectl configured with cluster access

**Expected Output**:
- Namespace `todo-dev` created and active
- ResourceQuota configured (CPU: 8 cores, Memory: 8Gi)
- LimitRange configured for default container limits
- Namespace labeled for monitoring

**Files to Create**:
- `k8s/namespace.yaml` - Namespace, ResourceQuota, LimitRange manifests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-002 (Minikube Deployment)
- Section: Technical Specifications → Kubernetes Resource Requirements

**Acceptance Criteria**:
- [ ] `kubectl get namespace todo-dev` shows Active status
- [ ] `kubectl get resourcequota -n todo-dev` shows configured quotas
- [ ] `kubectl get limitrange -n todo-dev` shows configured limits
- [ ] `kubectl get namespace todo-dev --show-labels` shows monitoring=enabled

---

## Containerization Tasks

### PH4-CTR-001: Create Frontend Dockerfile

**Task ID**: PH4-CTR-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Create multi-stage Dockerfile for React frontend with Nginx production server, ensuring image size < 250MB.

**Preconditions**:
- Frontend React application exists in `frontend/` directory
- Docker installed and running
- Frontend has package.json and build script configured

**Expected Output**:
- `frontend/Dockerfile` with multi-stage build (build + production stages)
- `frontend/.dockerignore` excluding node_modules, .git, etc.
- Docker image builds successfully
- Image size < 250MB
- Container runs as non-root user (nginx)
- Health check endpoint /health returns 200

**Files to Create**:
- `frontend/Dockerfile` - Multi-stage Docker build
- `frontend/.dockerignore` - Build context exclusions

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-001 (Docker Containerization)
- Section: Technical Specifications → Docker Image Requirements
- Section: Security Requirements → Image Security

**Acceptance Criteria**:
- [ ] `docker build -t todo-frontend:test ./frontend` completes successfully
- [ ] `docker images todo-frontend:test --format "{{.Size}}"` shows < 250MB
- [ ] `docker run -d -p 3000:80 todo-frontend:test` starts successfully
- [ ] `curl http://localhost:3000/health` returns 200 OK
- [ ] `docker run todo-frontend:test whoami` returns "nginx" (non-root)
- [ ] `docker scan todo-frontend:test` shows 0 critical vulnerabilities

---

### PH4-CTR-002: Create Backend Dockerfile

**Task ID**: PH4-CTR-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Create multi-stage Dockerfile for FastAPI backend with Dapr SDK integration, ensuring image size < 250MB.

**Preconditions**:
- Backend FastAPI application exists in `backend/` directory
- Docker installed and running
- Backend has requirements.txt with dependencies

**Expected Output**:
- `backend/Dockerfile` with multi-stage build (build + runtime stages)
- `backend/.dockerignore` excluding __pycache__, .git, venv, etc.
- Docker image builds successfully
- Image size < 250MB
- Health endpoints implemented: /health/live, /health/ready, /health/startup
- Dapr SDK included in dependencies
- Container runs as non-root user

**Files to Create**:
- `backend/Dockerfile` - Multi-stage Docker build
- `backend/.dockerignore` - Build context exclusions

**Files to Modify**:
- `backend/requirements.txt` - Add dapr-sdk dependency

**Related Spec Sections**:
- Section: Requirements → FR-IV-001 (Docker Containerization)
- Section: Technical Specifications → Docker Image Requirements
- Section: Health Checks Configuration

**Acceptance Criteria**:
- [ ] `docker build -t todo-backend:test ./backend` completes successfully
- [ ] `docker images todo-backend:test --format "{{.Size}}"` shows < 250MB
- [ ] `docker run -d -p 8000:8000 todo-backend:test` starts successfully
- [ ] `curl http://localhost:8000/health/live` returns 200 OK
- [ ] `curl http://localhost:8000/health/ready` returns 200 OK
- [ ] `curl http://localhost:8000/health/startup` returns 200 OK
- [ ] `docker run todo-backend:test pip show dapr-sdk` shows package installed
- [ ] `docker run todo-backend:test whoami` returns non-root user

---

### PH4-CTR-003: Implement Health Check Endpoints

**Task ID**: PH4-CTR-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Implement health check endpoints in FastAPI backend for Kubernetes liveness, readiness, and startup probes with dependency validation.

**Preconditions**:
- PH4-CTR-002 completed (Backend Dockerfile created)
- FastAPI backend application running
- Dapr SDK available for dependency checks

**Expected Output**:
- `/health/live` endpoint returns 200 when process is alive
- `/health/ready` endpoint returns 200 when all dependencies (Dapr, Redis, Kafka) are available
- `/health/ready` endpoint returns 503 when any dependency is unavailable
- `/health/startup` endpoint returns 200 after initialization complete
- All endpoints respond in < 100ms

**Files to Create**:
- `backend/health.py` - Health check endpoint implementations

**Files to Modify**:
- `backend/main.py` - Add health check routes
- `backend/requirements.txt` - Add any missing dependencies for health checks

**Related Spec Sections**:
- Section: Requirements → FR-IV-007 (Health Checks)
- Section: Technical Specifications → Health Checks Configuration
- Section: Acceptance Criteria → Health Checks

**Acceptance Criteria**:
- [ ] `curl http://localhost:8000/health/live` returns 200 OK
- [ ] `curl http://localhost:8000/health/ready` returns 200 OK (all deps up)
- [ ] `curl http://localhost:8000/health/ready` returns 503 (Redis down)
- [ ] `curl http://localhost:8000/health/startup` returns 200 OK
- [ ] Response time for all endpoints < 100ms (verified via curl -w "%{time_total}")

---

## Dapr Components Tasks

### PH4-DAPR-001: Configure Dapr Pub/Sub Component

**Task ID**: PH4-DAPR-001  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create and deploy Dapr pub/sub component configuration for Kafka message broker integration.

**Preconditions**:
- PH4-INF-003 completed (Dapr runtime installed)
- PH4-KAFKA-001 completed (Kafka installed)
- Kafka broker accessible at kafka-0.kafka-headless.todo-infra.svc.cluster.local:9092

**Expected Output**:
- Dapr pub/sub component YAML created with type: pubsub.kafka
- Component deployed to todo-dev namespace
- Component validated by Dapr operator
- Events can be published via Dapr API

**Files to Create**:
- `k8s/dapr-components/pubsub-kafka.yaml` - Dapr pub/sub component manifest

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-004 (Dapr Integration)
- Section: Technical Specifications → Dapr Component Configuration → Pub/Sub Component
- Section: Event-Driven Architecture

**Acceptance Criteria**:
- [ ] `kubectl get component kafka-pubsub -n todo-dev` shows component exists
- [ ] `dapr components -k -n todo-dev` lists kafka-pubsub with type pubsub.kafka
- [ ] `curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/todo.tasks -H "Content-Type: application/json" -d '{"type":"test","data":{}}'` returns 204 No Content

---

### PH4-DAPR-002: Configure Dapr State Store Component

**Task ID**: PH4-DAPR-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create and deploy Dapr state store component configuration for Redis with Kubernetes secret integration.

**Preconditions**:
- PH4-DAPR-001 completed (Dapr components configured)
- Redis installed and accessible
- Kubernetes secret created for Redis password

**Expected Output**:
- Dapr state store component YAML created with type: state.redis
- Redis host, port, and password (from secret) configured
- Component deployed to todo-dev namespace
- State can be saved and retrieved via Dapr API

**Files to Create**:
- `k8s/dapr-components/state-redis.yaml` - Dapr state store component manifest
- `k8s/secrets/redis-secret.yaml` - Redis password secret manifest

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-004 (Dapr Integration)
- Section: Technical Specifications → Dapr Component Configuration → State Store Component
- Section: Secrets Management

**Acceptance Criteria**:
- [ ] `kubectl get secret redis-secret -n todo-dev` shows secret exists
- [ ] `kubectl get component redis-state -n todo-dev` shows component exists
- [ ] `curl -X POST http://localhost:3500/v1.0/state/redis-state -H "Content-Type: application/json" -d '[{"key":"test","value":{"data":"test"}}]'` returns 204
- [ ] `curl http://localhost:3500/v1.0/state/redis-state/test` returns saved value

---

### PH4-DAPR-003: Configure Dapr Secret Store Component

**Task ID**: PH4-DAPR-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create and deploy Dapr secret store component for Kubernetes secrets integration, enabling secure secret retrieval.

**Preconditions**:
- PH4-DAPR-001 completed (Dapr components configured)
- Kubernetes cluster accessible
- RBAC permissions configured for secret access

**Expected Output**:
- Dapr secret store component YAML created with type: secretstores.kubernetes
- Component deployed to todo-dev namespace
- Secrets retrievable via Dapr API
- RBAC configured for least-privilege access

**Files to Create**:
- `k8s/dapr-components/secret-kubernetes.yaml` - Dapr secret store component manifest
- `k8s/rbac/dapr-secret-rbac.yaml` - RBAC configuration for Dapr

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-008 (Secrets Management)
- Section: Technical Specifications → Dapr Component Configuration
- Section: Security Requirements → Secrets Security

**Acceptance Criteria**:
- [ ] `kubectl get component kubernetes-secrets -n todo-dev` shows component exists
- [ ] `kubectl create secret generic test-secret --from-literal=password='test123' -n todo-dev` creates secret
- [ ] `curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/password` returns secret value

---

## Kafka Setup Tasks

### PH4-KAFKA-001: Install Kafka on Minikube

**Task ID**: PH4-KAFKA-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Install Kafka message broker on Minikube using Bitnami Helm chart in dedicated infrastructure namespace.

**Preconditions**:
- PH4-INF-002 completed (Minikube addons enabled)
- Helm 3.x installed
- Bitnami Helm repository accessible

**Expected Output**:
- Bitnami Helm repository added
- Kafka installed in todo-infra namespace with 1 broker replica
- Zookeeper installed with 1 replica
- Kafka headless service created
- Kafka accessible within cluster at kafka:9092

**Files to Create**:
- `k8s/infrastructure/kafka-values.yaml` - Kafka Helm chart values override

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-005 (Kafka Pub/Sub)
- Section: Technical Specifications → Kafka Pub/Sub Setup
- Section: Kafka Topic Definitions

**Acceptance Criteria**:
- [ ] `helm repo add bitnami https://charts.bitnami.com/bitnami` succeeds
- [ ] `helm install kafka bitnami/kafka -n todo-infra --set replicaCount=1` succeeds
- [ ] `kubectl get pods -n todo-infra -l app.kubernetes.io/name=kafka` shows kafka-0 Running
- [ ] `kubectl get pods -n todo-infra -l app.kubernetes.io/name=zookeeper` shows zookeeper-0 Running
- [ ] `kubectl get svc -n todo-infra kafka` shows service with port 9092

---

### PH4-KAFKA-002: Create Kafka Topics

**Task ID**: PH4-KAFKA-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create required Kafka topics for todo application event streaming with appropriate partitions and retention policies.

**Preconditions**:
- PH4-KAFKA-001 completed (Kafka installed and running)
- Kafka CLI tools accessible
- Kafka broker accessible

**Expected Output**:
- Topic `todo.tasks` created (3 partitions, replication=1, retention=7d)
- Topic `todo.chat` created (3 partitions, replication=1, retention=7d)
- Topic `todo.reminders` created (3 partitions, replication=1, retention=7d)
- Topic `todo.dead-letter` created (1 partition, replication=1, retention=30d)
- All topics verified via Kafka CLI

**Files to Create**:
- `k8s/jobs/kafka-topics-job.yaml` - Kubernetes Job to create topics

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Kafka Topic Definitions
- Section: Event Schema Definitions
- Section: Event-Driven Architecture

**Acceptance Criteria**:
- [ ] `kubectl exec -it kafka-0 -n todo-infra -- kafka-topics.sh --bootstrap-server localhost:9092 --list` shows all 4 topics
- [ ] `kubectl exec -it kafka-0 -n todo-infra -- kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic todo.tasks` shows Partitions: 3
- [ ] Test publish/consume succeeds on todo.tasks topic

---

## Helm Charts Tasks

### PH4-HELM-001: Create Helm Chart Structure

**Task ID**: PH4-HELM-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create complete Helm chart directory structure with Chart.yaml, values.yaml, templates, and helper functions.

**Preconditions**:
- PH4-CTR-003 completed (Health endpoints implemented)
- PH4-DAPR-002 completed (Dapr state store configured)
- PH4-DAPR-003 completed (Dapr secret store configured)
- Helm 3.x installed

**Expected Output**:
- Complete Helm chart directory structure created
- Chart.yaml with name: todo-app, version: 1.0.0, appVersion: 4.0.0
- values.yaml with 50+ configurable parameters
- values-dev.yaml with development environment overrides
- templates/_helpers.tpl with name, labels, selectors helpers
- templates/NOTES.txt with post-install instructions
- Helm lint passes with 0 errors

**Files to Create**:
- `charts/todo-app/Chart.yaml` - Chart metadata
- `charts/todo-app/values.yaml` - Default configuration values
- `charts/todo-app/values-dev.yaml` - Development overrides
- `charts/todo-app/templates/_helpers.tpl` - Template helpers
- `charts/todo-app/templates/NOTES.txt` - Post-install notes
- `charts/todo-app/templates/namespace.yaml` - Namespace template
- `charts/todo-app/templates/dapr-components/` - Dapr components directory
- `charts/todo-app/templates/services/` - Services directory
- `charts/todo-app/templates/infrastructure/` - Infrastructure directory
- `charts/todo-app/templates/observability/` - Observability directory

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-003 (Helm Charts)
- Section: Technical Specifications → Helm Chart Structure
- Section: Deployment Standards

**Acceptance Criteria**:
- [ ] `helm lint charts/todo-app` returns "1 chart(s) linted, 0 chart(s) failed"
- [ ] `helm show chart charts/todo-app` shows correct metadata
- [ ] `helm template todo-app charts/todo-app -f charts/todo-app/values-dev.yaml` renders valid Kubernetes YAML
- [ ] All required directories and files exist

---

### PH4-HELM-002: Create Frontend Deployment Template

**Task ID**: PH4-HELM-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create Kubernetes Deployment template for frontend service with Dapr sidecar annotations and resource configuration.

**Preconditions**:
- PH4-HELM-001 completed (Helm chart structure created)
- PH4-CTR-001 completed (Frontend Dockerfile created)

**Expected Output**:
- Frontend Deployment template with Dapr annotations
- Resource requests/limits configured from values.yaml
- ConfigMap references for nginx configuration
- Image pull policy configurable
- Pod anti-affinity for high availability

**Files to Create**:
- `charts/todo-app/templates/services/frontend/deployment.yaml` - Frontend deployment template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add frontend-specific values

**Related Spec Sections**:
- Section: Technical Specifications → Helm Chart Structure → Services
- Section: Dapr Sidecar Configuration

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/frontend/deployment.yaml` renders valid Deployment
- [ ] Dapr annotations present: dapr.io/enabled, dapr.io/app-id, dapr.io/app-port
- [ ] Resource requests and limits configured
- [ ] Pod anti-affinity rules present

---

### PH4-HELM-003: Create Backend Deployment Template

**Task ID**: PH4-HELM-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create Kubernetes Deployment template for backend API service with Dapr sidecar annotations and resource configuration.

**Preconditions**:
- PH4-HELM-001 completed (Helm chart structure created)
- PH4-CTR-002 completed (Backend Dockerfile created)

**Expected Output**:
- Backend Deployment template with Dapr annotations
- Resource requests/limits configured from values.yaml
- Environment variables from ConfigMap and Secrets
- Health check probes configured
- Pod anti-affinity for high availability

**Files to Create**:
- `charts/todo-app/templates/services/backend/deployment.yaml` - Backend deployment template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add backend-specific values

**Related Spec Sections**:
- Section: Technical Specifications → Helm Chart Structure → Services
- Section: Dapr Sidecar Configuration
- Section: Health Checks Configuration

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/backend/deployment.yaml` renders valid Deployment
- [ ] Dapr annotations present: dapr.io/enabled, dapr.io/app-id, dapr.io/app-port
- [ ] Resource requests and limits configured
- [ ] Health check probes configured from values

---

### PH4-HELM-004: Create Service Templates

**Task ID**: PH4-HELM-004  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create Kubernetes Service templates for frontend and backend with proper selectors and port configuration.

**Preconditions**:
- PH4-HELM-002 completed (Frontend deployment template created)
- PH4-HELM-003 completed (Backend deployment template created)

**Expected Output**:
- Frontend Service template (ClusterIP, port 80 → 3000)
- Backend Service template (ClusterIP, port 8000 → 8000)
- Service selectors match deployment labels
- Service types configurable via values.yaml

**Files to Create**:
- `charts/todo-app/templates/services/frontend/service.yaml` - Frontend service template
- `charts/todo-app/templates/services/backend/service.yaml` - Backend service template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add service configuration values

**Related Spec Sections**:
- Section: Technical Specifications → Helm Chart Structure → Services
- Section: Kubernetes Services and Ingress

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/frontend/service.yaml` renders valid Service
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/backend/service.yaml` renders valid Service
- [ ] Service selectors match deployment labels
- [ ] Port configuration correct

---

### PH4-HELM-005: Create Ingress Template

**Task ID**: PH4-HELM-005  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Create Kubernetes Ingress template with NGINX ingress class for external traffic routing.

**Preconditions**:
- PH4-INF-002 completed (Ingress addon enabled)
- PH4-HELM-004 completed (Service templates created)

**Expected Output**:
- Ingress template with NGINX ingress class
- Ingress rules: / → frontend, /api → backend
- SSL redirect annotation configured
- Host configurable via values.yaml

**Files to Create**:
- `charts/todo-app/templates/infrastructure/ingress.yaml` - Ingress template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add ingress configuration values

**Related Spec Sections**:
- Section: Technical Specifications → Helm Chart Structure → Infrastructure
- Section: Kubernetes Services and Ingress

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/infrastructure/ingress.yaml` renders valid Ingress
- [ ] NGINX ingress class annotation present
- [ ] Ingress rules configured for frontend and backend
- [ ] SSL redirect annotation configured

---

## Scaling Tasks

### PH4-SCALE-001: Configure Horizontal Pod Autoscaler

**Task ID**: PH4-SCALE-001  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure HPA templates for all microservices with CPU and memory-based autoscaling.

**Preconditions**:
- PH4-HELM-002 completed (Frontend deployment template)
- PH4-HELM-003 completed (Backend deployment template)
- PH4-INF-002 completed (Metrics-server addon enabled)

**Expected Output**:
- Frontend HPA template (min=2, max=4, CPU=70%, memory=80%)
- Backend HPA template (min=2, max=10, CPU=70%, memory=80%)
- Event-processor HPA template (min=2, max=6, CPU=70%, memory=80%)
- Scale-up stabilization: 60 seconds
- Scale-down stabilization: 300 seconds

**Files to Create**:
- `charts/todo-app/templates/services/frontend/hpa.yaml` - Frontend HPA template
- `charts/todo-app/templates/services/backend/hpa.yaml` - Backend HPA template
- `charts/todo-app/templates/services/event-processor/hpa.yaml` - Event processor HPA template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add HPA configuration values

**Related Spec Sections**:
- Section: Requirements → FR-IV-008 (Replica Scaling)
- Section: Technical Specifications → Horizontal Pod Autoscaler (HPA)
- Section: Scaling Strategy

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/backend/hpa.yaml` renders valid HPA
- [ ] Min/max replicas configured correctly
- [ ] CPU and memory targets configured (70%, 80%)
- [ ] Scale behavior policies configured

---

### PH4-SCALE-002: Configure Pod Disruption Budget

**Task ID**: PH4-SCALE-002  
**Priority**: P0  
**Estimated Hours**: 1

**Description**: Configure PDB templates for all services to ensure availability during voluntary disruptions.

**Preconditions**:
- PH4-HELM-002 completed (Frontend deployment template)
- PH4-HELM-003 completed (Backend deployment template)

**Expected Output**:
- Frontend PDB template (minAvailable=50%)
- Backend PDB template (minAvailable=50%)
- Event-processor PDB template (minAvailable=50%)
- PDB selector labels match deployment labels

**Files to Create**:
- `charts/todo-app/templates/services/frontend/pdb.yaml` - Frontend PDB template
- `charts/todo-app/templates/services/backend/pdb.yaml` - Backend PDB template
- `charts/todo-app/templates/services/event-processor/pdb.yaml` - Event processor PDB template

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Horizontal Pod Autoscaler (HPA)
- Section: Scaling Strategy

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/backend/pdb.yaml` renders valid PDB
- [ ] minAvailable: 50% configured
- [ ] Selector labels match deployment

---

## Health Checks Tasks

### PH4-HEALTH-001: Configure Kubernetes Probes

**Task ID**: PH4-HEALTH-001  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure liveness, readiness, and startup probe templates for all services in Helm charts.

**Preconditions**:
- PH4-CTR-003 completed (Health endpoints implemented)
- PH4-HELM-002 completed (Frontend deployment template)
- PH4-HELM-003 completed (Backend deployment template)

**Expected Output**:
- Liveness probe template (/health/live, initialDelay=10s, period=10s)
- Readiness probe template (/health/ready, initialDelay=5s, period=5s)
- Startup probe template (/health/startup, initialDelay=0s, period=5s, failureThreshold=12)
- Probe parameters configurable via values.yaml

**Files to Create**:
- `charts/todo-app/templates/services/frontend/probes.yaml` - Frontend probes template
- `charts/todo-app/templates/services/backend/probes.yaml` - Backend probes template
- `charts/todo-app/templates/services/event-processor/probes.yaml` - Event processor probes template

**Files to Modify**:
- `charts/todo-app/values.yaml` - Add probe configuration values
- `charts/todo-app/templates/services/frontend/deployment.yaml` - Reference probes template
- `charts/todo-app/templates/services/backend/deployment.yaml` - Reference probes template

**Related Spec Sections**:
- Section: Requirements → FR-IV-007 (Health Checks)
- Section: Technical Specifications → Health Checks Configuration

**Acceptance Criteria**:
- [ ] `helm template todo-app charts/todo-app --show-only templates/services/backend/deployment.yaml` shows all three probes configured
- [ ] Probe endpoints match implementation (/health/live, /health/ready, /health/startup)
- [ ] Probe parameters match specification

---

### PH4-HEALTH-002: Test Health Check Endpoints

**Task ID**: PH4-HEALTH-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Test all health check endpoints under various conditions including dependency failures.

**Preconditions**:
- PH4-HEALTH-001 completed (Probes configured)
- Application deployed to cluster
- All dependencies (Redis, Kafka, Dapr) running

**Expected Output**:
- Test report documenting health endpoint behavior
- Verification that readiness returns 503 when dependencies unavailable
- Response time measurements < 100ms
- Kubernetes probes functioning correctly (pod restarts on liveness failure)

**Files to Create**:
- `tests/health/health-check-tests.md` - Test report

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-007 (Health Checks)
- Section: Acceptance Criteria → Health Checks

**Acceptance Criteria**:
- [ ] All health endpoints return 200 when healthy
- [ ] Readiness returns 503 when Redis unavailable
- [ ] Readiness returns 503 when Kafka unavailable
- [ ] Response time < 100ms for all endpoints
- [ ] Pod restarts on liveness probe failure (verified via kubectl describe)

---

## Observability Tasks

### PH4-OBS-001: Deploy Prometheus and Grafana

**Task ID**: PH4-OBS-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Deploy Prometheus and Grafana stack for metrics collection and visualization using kube-prometheus-stack Helm chart.

**Preconditions**:
- PH4-INF-004 completed (Namespace created)
- Helm 3.x installed
- Prometheus community Helm repository accessible

**Expected Output**:
- kube-prometheus-stack installed in todo-dev namespace
- Prometheus running and scraping targets
- Grafana running with admin access
- ServiceMonitor created for todo-backend service
- ServiceMonitor created for Dapr sidecars
- Default dashboards accessible via Grafana UI

**Files to Create**:
- `k8s/observability/prometheus-values.yaml` - Prometheus stack values override
- `k8s/observability/backend-servicemonitor.yaml` - ServiceMonitor for backend
- `k8s/observability/dapr-servicemonitor.yaml` - ServiceMonitor for Dapr

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-010 (Observability)
- Section: Observability Requirements → Metrics
- Section: Technical Specifications → Helm Chart Structure → Observability

**Acceptance Criteria**:
- [ ] `kubectl get pods -n todo-dev -l app.kubernetes.io/name=prometheus` shows prometheus-* Running
- [ ] `kubectl get pods -n todo-dev -l app.kubernetes.io/name=grafana` shows grafana-* Running
- [ ] Grafana accessible via `kubectl port-forward svc/monitoring-grafana 3000:80`
- [ ] Prometheus targets include todo-backend and Dapr components
- [ ] Metrics accessible at http://todo-backend:8000/metrics

---

### PH4-OBS-002: Deploy Jaeger for Tracing

**Task ID**: PH4-OBS-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Deploy Jaeger for distributed tracing with Dapr integration for end-to-end request tracing.

**Preconditions**:
- PH4-OBS-001 completed (Prometheus/Grafana deployed)
- Dapr runtime installed
- Helm 3.x installed

**Expected Output**:
- Jaeger installed via Helm chart in todo-dev namespace
- Dapr configured to export traces to Jaeger (100% sampling for dev)
- Jaeger UI accessible
- Traces visible for service-to-service calls
- Trace includes spans for frontend, backend, Dapr sidecar, Kafka

**Files to Create**:
- `k8s/observability/jaeger-values.yaml` - Jaeger Helm values
- `k8s/dapr-components/tracing-config.yaml` - Dapr tracing configuration

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Observability Requirements → Tracing
- Section: Technical Specifications → Dapr Sidecar Configuration

**Acceptance Criteria**:
- [ ] `kubectl get pods -l app.kubernetes.io/name=jaeger -n todo-dev` shows jaeger-* Running
- [ ] Jaeger UI accessible via `kubectl port-forward svc/jaeger-query 16686:16686`
- [ ] Traces visible after making API requests
- [ ] Traces include multiple spans (frontend, backend, Dapr, Kafka)

---

### PH4-OBS-003: Deploy Loki for Logging

**Task ID**: PH4-OBS-003  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Deploy Loki and Fluent Bit for log aggregation with Grafana integration for centralized log searching.

**Preconditions**:
- PH4-OBS-001 completed (Grafana deployed)
- Helm 3.x installed
- Grafana Helm repository accessible

**Expected Output**:
- Loki stack installed via Helm in todo-dev namespace
- Fluent Bit deployed as DaemonSet on all nodes
- Fluent Bit configured to send logs to Loki
- Logs searchable in Grafana Explore interface
- Log retention configured for 30 days

**Files to Create**:
- `k8s/observability/loki-values.yaml` - Loki stack Helm values
- `k8s/observability/fluentbit-config.yaml` - Fluent Bit configuration

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Observability Requirements → Logging
- Section: Technical Specifications → Helm Chart Structure → Observability

**Acceptance Criteria**:
- [ ] `kubectl get pods -l app.kubernetes.io/name=loki -n todo-dev` shows loki-* Running
- [ ] `kubectl get pods -l app.kubernetes.io/name=fluent-bit -n todo-dev` shows fluent-bit-* Running
- [ ] Logs searchable in Grafana Explore with Loki datasource
- [ ] Query `{app="todo-backend"}` returns backend logs

---

## CI/CD Tasks

### PH4-CICD-001: Create GitHub Actions Workflow

**Task ID**: PH4-CICD-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Create GitHub Actions CI/CD workflow for automated build, test, security scan, and deployment.

**Preconditions**:
- PH4-CTR-003 completed (Health endpoints implemented)
- GitHub repository configured
- GitHub Actions enabled

**Expected Output**:
- `.github/workflows/ci-cd.yaml` workflow file created
- Workflow triggers on push to main/develop and pull requests
- Test job runs pytest with coverage reporting
- Build job creates Docker images and pushes to GHCR
- Security scan job runs Trivy vulnerability scanning
- Deploy job deploys to Minikube using Helm
- Pipeline completes in <10 minutes

**Files to Create**:
- `.github/workflows/ci-cd.yaml` - CI/CD workflow definition

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-IV-009 (GitHub Actions CI/CD)
- Section: Technical Specifications → GitHub Actions Pipeline
- Section: CI/CD Flow

**Acceptance Criteria**:
- [ ] Workflow file exists at `.github/workflows/ci-cd.yaml`
- [ ] `yamllint .github/workflows/ci-cd.yaml` passes
- [ ] Workflow triggers on PR creation
- [ ] All jobs (test, build, security-scan, deploy) pass
- [ ] Docker images pushed to GHCR with SHA tags
- [ ] Pipeline completes in <10 minutes

---

### PH4-CICD-002: Configure GitHub Container Registry

**Task ID**: PH4-CICD-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure GitHub Container Registry (GHCR) for Docker image storage with proper authentication and tagging.

**Preconditions**:
- PH4-CICD-001 completed (GitHub Actions workflow created)
- GitHub repository has GHCR enabled
- GitHub Actions configured with GITHUB_TOKEN permissions

**Expected Output**:
- GHCR enabled in repository settings
- GitHub Actions workflow configured to login to GHCR
- Images tagged with commit SHA
- Images tagged with branch name
- Package visibility configured (public or organization)

**Files to Create**:
- None

**Files to Modify**:
- `.github/workflows/ci-cd.yaml` - Add GHCR login and push steps

**Related Spec Sections**:
- Section: Technical Specifications → GitHub Actions Pipeline
- Section: CI/CD Flow

**Acceptance Criteria**:
- [ ] Workflow includes GHCR login step
- [ ] Images pushed to ghcr.io/<owner>/todo-frontend and ghcr.io/<owner>/todo-backend
- [ ] Images tagged with commit SHA (e.g., abc1234)
- [ ] Images tagged with branch name (e.g., main, develop)
- [ ] GHCR UI shows packages at https://ghcr.io/<owner>

---

### PH4-CICD-003: Configure Environment Protection

**Task ID**: PH4-CICD-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure GitHub environment protection rules for development, staging, and production deployments with appropriate approval workflows.

**Preconditions**:
- PH4-CICD-001 completed (GitHub Actions workflow created)
- GitHub repository admin access

**Expected Output**:
- Development environment configured (auto-deploy on merge to develop)
- Staging environment configured (auto-deploy on tag)
- Production environment configured (manual approval required)
- Required reviewers configured for production (2 reviewers)
- Wait timer configured for production (5 minutes)
- Deployment branches restricted per environment

**Files to Create**:
- None (GitHub UI configuration)

**Files to Modify**:
- `.github/workflows/ci-cd.yaml` - Add environment contexts to deploy jobs

**Related Spec Sections**:
- Section: Technical Specifications → GitHub Actions Pipeline
- Section: Deployment Standards

**Acceptance Criteria**:
- [ ] Development, staging, production environments exist in GitHub Settings
- [ ] Merge to develop triggers auto-deploy to development
- [ ] Merge to main triggers deployment requiring manual approval
- [ ] Production deployment requires 2 reviewer approvals
- [ ] Production deployment has 5-minute wait timer

---

## Security Tasks

### PH4-SEC-001: Configure Network Policies

**Task ID**: PH4-SEC-001  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure Kubernetes NetworkPolicies for zero-trust network security model with default deny and explicit allow rules.

**Preconditions**:
- PH4-INF-002 completed (Minikube addons enabled with ingress)
- Network policy controller available (Calico or similar)

**Expected Output**:
- Default deny-all NetworkPolicy created
- Frontend allow policy: ingress from ingress-nginx, egress to backend
- Backend allow policy: ingress from frontend, egress to Kafka, Redis, Dapr
- Dapr sidecar communication allowed
- Kafka and Redis internal only (no external access)

**Files to Create**:
- `k8s/security/networkpolicies.yaml` - NetworkPolicy manifests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Security Requirements → Network Security
- Section: Technical Specifications → Helm Chart Structure → Infrastructure

**Acceptance Criteria**:
- [ ] `kubectl get networkpolicies -n todo-dev` shows default-deny, frontend-allow, backend-allow
- [ ] Unauthorized pod cannot access backend (connection refused)
- [ ] Frontend pod can access backend (connection succeeds)
- [ ] Backend pod can access Kafka and Redis

---

### PH4-SEC-002: Configure Pod Security Standards

**Task ID**: PH4-SEC-002  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Configure Pod Security Standards and security contexts for all deployments to enforce security best practices.

**Preconditions**:
- PH4-HELM-002 completed (Frontend deployment template)
- PH4-HELM-003 completed (Backend deployment template)
- Kubernetes cluster with Pod Security Admission enabled

**Expected Output**:
- Namespace labeled: pod-security.kubernetes.io/enforce=baseline
- All deployment templates include securityContext
- runAsNonRoot: true configured
- readOnlyRootFilesystem: true configured
- allowPrivilegeEscalation: false configured
- capabilities.drop: ["ALL"] configured

**Files to Create**:
- `k8s/security/pod-security-standards.yaml` - Namespace labels and security contexts

**Files to Modify**:
- `charts/todo-app/templates/services/frontend/deployment.yaml` - Add securityContext
- `charts/todo-app/templates/services/backend/deployment.yaml` - Add securityContext
- `charts/todo-app/values.yaml` - Add security configuration values

**Related Spec Sections**:
- Section: Security Requirements → Image Security
- Section: Technical Specifications → Kubernetes Manifest Requirements

**Acceptance Criteria**:
- [ ] `kubectl get ns todo-dev --show-labels` shows pod-security.kubernetes.io/enforce=baseline
- [ ] `kubectl get pod todo-backend-abc123 -n todo-dev -o jsonpath='{.spec.securityContext}'` shows runAsNonRoot=true
- [ ] Attempting to deploy pod with root user fails with policy violation

---

## Testing Tasks

### PH4-TEST-001: Integration Testing

**Task ID**: PH4-TEST-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create and execute integration tests for Dapr pub/sub, state store, and service-to-service communication.

**Preconditions**:
- PH4-HELM-002 completed (Frontend deployed)
- PH4-HELM-003 completed (Backend deployed)
- PH4-DAPR-002 completed (Dapr state store configured)
- PH4-DAPR-001 completed (Dapr pub/sub configured)
- pytest installed

**Expected Output**:
- Integration test suite in `tests/integration/`
- Test for Dapr pub/sub publish
- Test for Dapr pub/sub subscribe
- Test for Dapr state save/get
- Test for service-to-service invocation
- All tests pass with 100% success rate

**Files to Create**:
- `tests/integration/conftest.py` - Pytest fixtures
- `tests/integration/test_dapr_pubsub.py` - Pub/sub tests
- `tests/integration/test_dapr_state.py` - State store tests
- `tests/integration/test_service_invocation.py` - Service invocation tests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Testing Requirements → Integration Tests
- Section: Acceptance Criteria → Integration Tests

**Acceptance Criteria**:
- [ ] `pytest tests/integration -v` runs successfully
- [ ] All pub/sub tests pass
- [ ] All state store tests pass
- [ ] All service invocation tests pass
- [ ] Test coverage report generated

---

### PH4-TEST-002: End-to-End Testing

**Task ID**: PH4-TEST-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create and execute end-to-end tests for complete user workflows including task CRUD operations and event-driven persistence.

**Preconditions**:
- PH4-TEST-001 completed (Integration tests passing)
- Full application deployed to cluster
- All services healthy

**Expected Output**:
- E2E test suite in `tests/e2e/`
- Test for complete task creation flow
- Test for task listing flow
- Test for task update flow
- Test for task deletion flow
- Test for event-driven persistence
- All tests pass

**Files to Create**:
- `tests/e2e/conftest.py` - E2E test fixtures
- `tests/e2e/test_task_crud.py` - CRUD operation tests
- `tests/e2e/test_event_flow.py` - Event flow tests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Testing Requirements → Integration Tests
- Section: Acceptance Criteria → Integration Tests

**Acceptance Criteria**:
- [ ] `pytest tests/e2e -v` runs successfully
- [ ] Task creation flow test passes (create → event published → persisted → retrievable)
- [ ] Task listing flow test passes
- [ ] Task update flow test passes
- [ ] Task deletion flow test passes
- [ ] Event flow test verifies Kafka events published

---

### PH4-TEST-003: Load Testing

**Task ID**: PH4-TEST-003  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Perform load testing to validate HPA scaling behavior and performance under load with 100 concurrent users.

**Preconditions**:
- PH4-TEST-001 completed (Integration tests passing)
- Application deployed with HPA configured
- k6 or similar load testing tool installed
- Metrics server running

**Expected Output**:
- k6 load test script created
- Test scenario: 100 concurrent users for 5 minutes
- HPA scales up under load (verified via kubectl)
- P95 latency < 500ms
- Error rate < 1%
- Load test report with findings

**Files to Create**:
- `tests/load/task-load-test.js` - k6 load test script
- `tests/load/load-test-report.md` - Load test findings report

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Testing Requirements → Performance Tests
- Section: Scaling Strategy

**Acceptance Criteria**:
- [ ] `k6 run tests/load/task-load-test.js` completes successfully
- [ ] k6 summary shows checks: 100% passed
- [ ] k6 summary shows http_req_duration p(95) < 500ms
- [ ] `kubectl get hpa -n todo-dev` shows CURRENT replicas increased under load
- [ ] Error rate < 1% throughout test
- [ ] Load test report documents findings and recommendations

---

## Documentation Tasks

### PH4-DOC-001: Create Deployment Documentation

**Task ID**: PH4-DOC-001  
**Priority**: P1  
**Estimated Hours**: 3

**Description**: Create comprehensive deployment and operations documentation for Phase IV including deployment guide, architecture overview, configuration reference, troubleshooting, and runbooks.

**Preconditions**:
- All PH4-* tasks completed (or near completion)
- Application successfully deployed to Minikube
- All tests passing

**Expected Output**:
- DEPLOYMENT.md: Step-by-step deployment guide with prerequisites
- ARCHITECTURE.md: Architecture overview with Mermaid diagrams
- CONFIGURATION.md: All configuration parameters documented
- TROUBLESHOOTING.md: Common issues and solutions
- RUNBOOK.md: Operational procedures (scaling, backup, recovery)

**Files to Create**:
- `docs/phase-iv/DEPLOYMENT.md` - Deployment guide
- `docs/phase-iv/ARCHITECTURE.md` - Architecture documentation
- `docs/phase-iv/CONFIGURATION.md` - Configuration reference
- `docs/phase-iv/TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/phase-iv/RUNBOOK.md` - Operational runbooks

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Documentation Standards

**Acceptance Criteria**:
- [ ] All documentation files exist in `docs/phase-iv/`
- [ ] DEPLOYMENT.md tested by following steps (deployment succeeds)
- [ ] ARCHITECTURE.md includes system context and component diagrams
- [ ] CONFIGURATION.md documents all values.yaml parameters
- [ ] TROUBLESHOOTING.md includes at least 10 common issues
- [ ] RUNBOOK.md includes scaling, backup, and recovery procedures

---

## Task Dependency Graph

```
PH4-INF-001 (Setup Minikube)
├── PH4-INF-002 (Enable Addons)
│   ├── PH4-INF-004 (Create Namespace)
│   ├── PH4-KAFKA-001 (Install Kafka)
│   │   └── PH4-KAFKA-002 (Create Topics)
│   ├── PH4-SEC-001 (Network Policies)
│   └── PH4-OBS-001 (Prometheus/Grafana)
│       ├── PH4-OBS-002 (Jaeger)
│       └── PH4-OBS-003 (Loki)
└── PH4-INF-003 (Install Dapr)
    ├── PH4-DAPR-001 (Pub/Sub)
    │   ├── PH4-DAPR-002 (State Store)
    │   └── PH4-DAPR-003 (Secret Store)
    └── PH4-KAFKA-001

PH4-CTR-001 (Frontend Dockerfile)
└── PH4-CTR-003 (Health Endpoints)

PH4-CTR-002 (Backend Dockerfile)
└── PH4-CTR-003

PH4-CTR-003 (Health Endpoints)
├── PH4-HELM-001 (Helm Structure)
│   ├── PH4-HELM-002 (Frontend Deployment)
│   ├── PH4-HELM-003 (Backend Deployment)
│   ├── PH4-HELM-004 (Service Templates)
│   │   └── PH4-HELM-005 (Ingress Template)
│   ├── PH4-SCALE-001 (HPA)
│   │   └── PH4-SCALE-002 (PDB)
│   └── PH4-HEALTH-001 (Probes)
│       └── PH4-HEALTH-002 (Test Health)
├── PH4-CICD-001 (GitHub Actions)
│   ├── PH4-CICD-002 (GHCR)
│   └── PH4-CICD-003 (Environment Protection)
└── PH4-SEC-002 (Pod Security)

PH4-HELM-002/003/004/005 (Helm Templates)
└── PH4-TEST-001 (Integration Tests)
    ├── PH4-TEST-002 (E2E Tests)
    └── PH4-TEST-003 (Load Tests)

PH4-TEST-002
└── PH4-DOC-001 (Documentation)
```

---

## Critical Path

**Critical Path**: PH4-INF-001 → PH4-INF-003 → PH4-DAPR-001 → PH4-DAPR-002 → PH4-HELM-001 → PH4-HELM-002/003 → PH4-TEST-001 → PH4-TEST-002 → PH4-DOC-001

**Total Critical Path Duration**: ~32 hours

---

**Version**: 1.0.0  
**Created**: 2026-03-12  
**Status**: Ready for Implementation  
**Next**: Begin task execution starting with Infrastructure tasks (PH4-INF-001)
