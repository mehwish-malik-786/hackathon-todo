# Phase V: Advanced Cloud Deployment Specification

## Feature Overview

**Feature Name**: Phase V - Advanced Cloud Deployment  
**Phase**: Phase V (Production Cloud + Advanced Features)  
**Priority**: P0 (Production Release)  
**Status**: Draft  
**Constitution**: `.specify/memory/phase-iv-v-constitution.md`  
**Prerequisite**: Phase IV (Local Kubernetes)

---

## Executive Summary

Phase V extends Phase IV with advanced todo features (recurring tasks, due dates, reminders, priorities, tags, search, filter), migrates deployment to cloud Kubernetes (AKS/GKE), implements production-grade CI/CD, and establishes comprehensive monitoring and logging.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-V-001 | Recurring Tasks | P0 | Support daily, weekly, monthly, yearly, custom recurrence patterns |
| FR-V-002 | Due Dates | P0 | Tasks can have due dates with timezone support |
| FR-V-003 | Reminders | P0 | Configurable reminders before due date (email, push, in-app) |
| FR-V-004 | Priority Levels | P0 | Low, Medium, High, Urgent priority for tasks |
| FR-V-005 | Tags | P0 | Multi-tag support for task organization |
| FR-V-006 | Search | P0 | Full-text search across tasks (title, description, tags) |
| FR-V-007 | Filter | P0 | Filter by status, priority, tags, due date, date range |
| FR-V-008 | Event-Driven Kafka Architecture | P0 | All features use Kafka event streaming |
| FR-V-009 | Dapr Jobs API | P1 | Scheduled tasks via Dapr Cron binding |
| FR-V-010 | Cloud Kubernetes (AKS/GKE) | P0 | Production deployment on Azure AKS or Google GKE |
| FR-V-011 | Production CI/CD | P0 | Multi-environment pipeline (dev → staging → prod) |
| FR-V-012 | Monitoring & Logging | P0 | Production-grade observability with alerting |

### Non-Functional Requirements

| ID | Requirement | Target | Description |
|----|-------------|--------|-------------|
| NFR-V-001 | Availability | 99.9% | Production SLA |
| NFR-V-002 | Latency | <300ms | API response time (P95) |
| NFR-V-003 | Throughput | 1000 req/sec | Sustained request handling |
| NFR-V-004 | Data Durability | 99.999% | Event persistence guarantee |
| NFR-V-005 | Recovery Time | <5 min | RTO (Recovery Time Objective) |
| NFR-V-006 | Recovery Point | <1 min | RPO (Recovery Point Objective) |
| NFR-V-007 | Scalability | 10,000 users | Support user base |
| NFR-V-008 | Search Latency | <100ms | Full-text search response |

---

## User Journeys

### Journey 1: Recurring Task Creation

```
User Story: As a user, I want to create recurring tasks
            so I don't have to manually recreate routine tasks.

Steps:
1. User opens task creation form
2. User enters: "Weekly team meeting"
3. User sets recurrence: Weekly (every Monday at 10:00 AM)
4. User sets priority: High
5. User adds tags: work, meeting
6. User saves task
7. Backend publishes: task.created (with recurrence rule)
8. Event Processor stores task + schedules next occurrence via Dapr Jobs
9. Dapr Jobs triggers at scheduled time
10. New task instance created for current week
11. User receives notification: "Weekly team meeting created for this week"

Expected Outcome:
- Recurring task created with RRULE
- Automatic instance generation
- User notified each occurrence
```

**Event Schema: task.created (with recurrence)**
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "time": "2026-03-12T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "task:10",
  "data": {
    "task_id": 10,
    "title": "Weekly team meeting",
    "description": "Sync with the team",
    "priority": "high",
    "tags": ["work", "meeting"],
    "status": "pending",
    "recurrence": {
      "enabled": true,
      "pattern": "FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0",
      "timezone": "America/New_York"
    },
    "created_by": "user-123",
    "created_at": "2026-03-12T10:30:00Z"
  }
}
```

---

### Journey 2: Due Date with Reminder

```
User Story: As a user, I want to set due dates and reminders
            so I never miss important deadlines.

Steps:
1. User creates task: "Submit project report"
2. User sets due date: March 20, 2026 at 5:00 PM
3. User configures reminders: 1 day before, 1 hour before
4. Task saved with due date and reminder rules
5. Dapr Jobs schedules reminder jobs
6. March 19, 5:00 PM: First reminder triggers
7. System sends email notification
8. March 20, 4:00 PM: Second reminder triggers
9. System sends push notification
10. March 20, 5:00 PM: Task becomes overdue if not completed
11. System sends overdue notification

Expected Outcome:
- Due date tracked with timezone
- Reminders sent at configured times
- Overdue detection and notification
```

**Event Schema: task.reminder.triggered**
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.reminder.triggered",
  "source": "/dapr-jobs",
  "id": "550e8400-e29b-41d4-a716-446655440011",
  "time": "2026-03-19T17:00:00Z",
  "datacontenttype": "application/json",
  "subject": "task:11:reminder",
  "data": {
    "task_id": 11,
    "title": "Submit project report",
    "reminder_type": "email",
    "due_date": "2026-03-20T17:00:00-05:00",
    "time_until_due": "24h",
    "user_id": "user-123",
    "user_email": "user@example.com"
  }
}
```

---

### Journey 3: Priority and Tags Organization

```
User Story: As a user, I want to organize tasks with priority and tags
            so I can focus on what matters most.

Steps:
1. User views task list
2. User filters by priority: Urgent
3. System shows only urgent tasks
4. User adds tag filter: work
5. System shows urgent work tasks
6. User sorts by due date
7. User completes top priority task
8. System updates task status via event

Expected Outcome:
- Tasks organized by priority
- Multi-tag filtering works
- Fast filter response (<100ms)
```

**Event Schema: task.filtered**
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.filtered",
  "source": "/todo-query",
  "id": "550e8400-e29b-41d4-a716-446655440012",
  "time": "2026-03-12T11:00:00Z",
  "datacontenttype": "application/json",
  "subject": "user:user-123:filter",
  "data": {
    "user_id": "user-123",
    "filters": {
      "priority": ["urgent"],
      "tags": ["work"],
      "status": ["pending"],
      "due_date_range": {
        "start": "2026-03-12",
        "end": "2026-03-31"
      }
    },
    "result_count": 5,
    "query_time_ms": 45
  }
}
```

---

### Journey 4: Full-Text Search

```
User Story: As a user, I want to search my tasks
            so I can quickly find what I'm looking for.

Steps:
1. User enters search: "quarterly review presentation"
2. Frontend calls search API
3. Query Service searches Elasticsearch index
4. Results returned ranked by relevance
5. User sees matching tasks highlighted
6. User clicks result to view task

Expected Outcome:
- Full-text search across title, description, tags
- Results ranked by relevance
- Search completes in <100ms
- Highlighting of matched terms
```

**Event Schema: task.searched**
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.searched",
  "source": "/todo-query",
  "id": "550e8400-e29b-41d4-a716-446655440013",
  "time": "2026-03-12T11:30:00Z",
  "datacontenttype": "application/json",
  "subject": "user:user-123:search",
  "data": {
    "user_id": "user-123",
    "query": "quarterly review presentation",
    "result_count": 3,
    "query_time_ms": 67,
    "results": [
      {
        "task_id": 15,
        "title": "Q1 Quarterly Review Presentation",
        "score": 0.95
      },
      {
        "task_id": 12,
        "title": "Prepare review slides",
        "score": 0.72
      }
    ]
  }
}
```

---

### Journey 5: Cloud Migration (Minikube → AKS/GKE)

```
User Story: As a DevOps engineer, I want to migrate to cloud Kubernetes
            so we have production-grade infrastructure.

Steps:
1. Create AKS/GKE cluster with Terraform
2. Configure cloud-specific Helm values (values-aks.yaml)
3. Update Dapr components for managed services:
   - Redis → Azure Cache for Redis / Memorystore
   - Kafka → Confluent Cloud
   - Secrets → Azure Key Vault / GCP Secret Manager
4. Set up ingress with TLS (cert-manager)
5. Configure monitoring (Azure Monitor / Cloud Monitoring)
6. Run smoke tests
7. Update DNS to point to cloud ingress
8. Cutover traffic
9. Monitor for issues
10. Decommission Minikube (optional)

Expected Outcome:
- Zero-downtime migration
- All services operational in cloud
- Monitoring and alerting active
- Performance meets SLA targets
```

---

### Journey 6: Production Incident Response

```
User Story: As an SRE, I want comprehensive monitoring and alerting
            so I can quickly identify and resolve issues.

Steps:
1. Backend service latency spikes (P95 > 500ms)
2. Prometheus detects threshold breach
3. Alertmanager triggers PagerDuty alert
4. On-call engineer receives notification
5. Engineer opens Grafana dashboard
6. Dashboard shows increased error rate on task-command service
7. Engineer checks Jaeger traces
8. Trace reveals slow Kafka consumer
9. Engineer scales event-processor service (kubectl-ai scale deployment event-processor --replicas=6)
10. Latency returns to normal
11. Alert resolves automatically
12. Incident logged in post-mortem

Expected Outcome:
- Alert triggered within 1 minute
- Root cause identified in <5 minutes
- Resolution in <10 minutes
- No customer impact
```

---

## Technical Specifications

### Kafka Topic Definitions (Extended)

| Topic | Partitions | Replication | Retention | Purpose |
|-------|------------|-------------|-----------|---------|
| `todo.tasks` | 6 | 3 | 30 days | Task CRUD events |
| `todo.tasks.recurrence` | 3 | 3 | 30 days | Recurring task events |
| `todo.reminders` | 6 | 3 | 30 days | Reminder trigger events |
| `todo.search` | 3 | 3 | 7 days | Search indexing events |
| `todo.notifications` | 6 | 3 | 30 days | Notification events |
| `todo.chat` | 3 | 3 | 30 days | Chat message events |
| `todo.audit` | 3 | 3 | 90 days | Audit log events |
| `todo.dead-letter` | 3 | 3 | 90 days | Failed events |

### Extended Event Schema Definitions

#### task.created (with all features)
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440020",
  "time": "2026-03-12T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "task:20",
  "data": {
    "task_id": 20,
    "title": "Submit quarterly report",
    "description": "Complete Q1 financial report",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "finance", "quarterly"],
    "due_date": "2026-03-31T17:00:00-05:00",
    "recurrence": {
      "enabled": true,
      "pattern": "FREQ=YEARLY;BYMONTH=3;BYMONTHDAY=31",
      "timezone": "America/New_York"
    },
    "reminders": [
      {
        "type": "email",
        "offset": "7d"
      },
      {
        "type": "push",
        "offset": "1d"
      }
    ],
    "created_by": "user-123",
    "created_at": "2026-03-12T10:30:00Z"
  }
}
```

#### task.updated (with field-level changes)
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.updated",
  "source": "/todo-backend",
  "id": "550e8400-e29b-41d4-a716-446655440021",
  "time": "2026-03-15T14:00:00Z",
  "datacontenttype": "application/json",
  "subject": "task:20",
  "data": {
    "task_id": 20,
    "title": "Submit quarterly report",
    "priority": "urgent",
    "tags": ["work", "finance", "quarterly", "urgent"],
    "status": "in_progress",
    "updated_by": "user-123",
    "updated_at": "2026-03-15T14:00:00Z",
    "changes": [
      {
        "field": "priority",
        "old_value": "high",
        "new_value": "urgent"
      },
      {
        "field": "tags",
        "old_value": ["work", "finance", "quarterly"],
        "new_value": ["work", "finance", "quarterly", "urgent"]
      },
      {
        "field": "status",
        "old_value": "pending",
        "new_value": "in_progress"
      }
    ]
  }
}
```

#### task.overdue
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.overdue",
  "source": "/dapr-jobs",
  "id": "550e8400-e29b-41d4-a716-446655440022",
  "time": "2026-04-01T00:00:00Z",
  "datacontenttype": "application/json",
  "subject": "task:20:overdue",
  "data": {
    "task_id": 20,
    "title": "Submit quarterly report",
    "due_date": "2026-03-31T17:00:00-05:00",
    "overdue_by": "7h",
    "status": "pending",
    "priority": "urgent",
    "user_id": "user-123"
  }
}
```

#### task.search.index
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.search.index",
  "source": "/event-processor",
  "id": "550e8400-e29b-41d4-a716-446655440023",
  "time": "2026-03-12T10:30:01Z",
  "datacontenttype": "application/json",
  "subject": "task:20:index",
  "data": {
    "task_id": 20,
    "title": "Submit quarterly report",
    "description": "Complete Q1 financial report",
    "tags": ["work", "finance", "quarterly"],
    "priority": "high",
    "status": "pending",
    "user_id": "user-123",
    "indexed_at": "2026-03-12T10:30:01Z"
  }
}
```

### Dapr Jobs API Configuration

#### Cron Binding for Recurring Tasks
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: recurring-tasks-cron
  namespace: todo-prod
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "0 */5 * * * *"  # Every 5 minutes (configurable)
  - name: direction
    value: "input"
```

#### Recurring Task Processor Service
```python
@app.route('/recurring-tasks', methods=['POST'])
@dapr_app.subscribe('recurring-tasks-cron')
def process_recurring_tasks():
    """Check for recurring tasks that need new instances created."""
    # Query tasks with recurrence rules
    recurring_tasks = get_due_recurring_tasks()
    
    for task in recurring_tasks:
        # Create new instance for current period
        new_task = create_task_instance(task)
        
        # Publish event
        publish_event('task.created', {
            'task_id': new_task.id,
            'parent_task_id': task.id,
            'title': task.title,
            'recurrence_instance': True
        })
    
    return 'OK'
```

### Cloud Kubernetes Deployment (AKS/GKE)

#### AKS Cluster Configuration (Terraform)
```hcl
resource "azurerm_kubernetes_cluster" "todo" {
  name                = "todo-aks-prod"
  location            = "eastus"
  resource_group_name = "todo-prod-rg"
  dns_prefix          = "todoprod"
  kubernetes_version  = "1.28"

  default_node_pool {
    name       = "system"
    node_count = 3
    vm_size    = "Standard_DS2_v2"
    zones      = [1, 2, 3]
  }

  identity {
    type = "SystemAssigned"
  }

  addon_profile {
    oms_agent {
      enabled = true
    }
    ingress_application_gateway {
      enabled = true
    }
  }
}

resource "azurerm_redis_cache" "todo" {
  name                = "todo-redis-prod"
  location            = "eastus"
  resource_group_name = "todo-prod-rg"
  capacity            = 2
  family              = "P"
  sku_name            = "Premium"
  
  redis_configuration {
    maxmemory_reserved = "2000"
  }
}
```

#### GKE Cluster Configuration (Terraform)
```hcl
resource "google_container_cluster" "todo" {
  name     = "todo-gke-prod"
  location = "us-central1"
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  networking_mode = "VPC_NATIVE"
  
  release_channel {
    channel = "REGULAR"
  }
}

resource "google_container_node_pool" "todo" {
  name       = "todo-nodes"
  location   = "us-central1"
  cluster    = google_container_cluster.todo.name
  node_count = 3
  
  node_config {
    machine_type = "e2-standard-2"
    
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
  
  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }
}

resource "google_redis_instance" "todo" {
  name           = "todo-redis-prod"
  tier           = "STANDARD_HA"
  memory_size_gb = 2
  region         = "us-central1"
}
```

### Helm Values for Cloud (values-aks.yaml)

```yaml
# Azure AKS specific values
global:
  environment: production
  cloud: azure

ingress:
  class: azure-application-gateway
  tls:
    enabled: true
    secretName: todo-tls-secret
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"

dapr:
  components:
    statestore:
      type: azure.redis
      host: todo-redis-prod.redis.cache.windows.net
      port: 6380
      ssl: true
      password:
        secretKeyRef:
          name: redis-secret
          key: password
    
    pubsub:
      type: kafka
      brokers:
        - "pkc-xyz123.eastus.azure.confluent.cloud:9092"
      sasl:
        enabled: true
        mechanism: PLAIN
        user:
          secretKeyRef:
            name: kafka-secret
            key: username
        password:
          secretKeyRef:
            name: kafka-secret
            key: password
      ssl:
        enabled: true
    
    secretstore:
      type: azure.keyvault
      vaultName: todo-prod-kv
      tenantId:
        secretKeyRef:
          name: azure-secret
          key: tenant-id

monitoring:
  prometheus:
    enabled: false  # Use Azure Monitor instead
  grafana:
    enabled: true
  jaeger:
    enabled: true

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilization: 70
  targetMemoryUtilization: 80

resources:
  frontend:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  backend:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
```

### Production CI/CD Pipeline (Multi-Environment)

```yaml
name: Production CI/CD Pipeline

on:
  push:
    branches: [main]
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
    - name: Trivy scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ needs.build.outputs.version }}
        format: 'sarif'
        output: 'trivy-backend.sarif'
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v3

  deploy-dev:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    environment: development
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to Dev (Minikube)
      run: |
        helm upgrade --install todo-app ./charts/todo-app \
          -f charts/todo-app/values-dev.yaml \
          --set image.tag=${{ needs.build.outputs.version }} \
          --namespace todo-dev \
          --create-namespace \
          --wait

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to Staging (AKS/GKE)
      run: |
        helm upgrade --install todo-app ./charts/todo-app \
          -f charts/todo-app/values-staging.yaml \
          --set image.tag=${{ needs.build.outputs.version }} \
          --namespace todo-staging \
          --create-namespace \
          --atomic \
          --timeout 10m
    - name: Run integration tests
      run: pytest tests/integration/ -v --staging

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to Production (AKS/GKE)
      run: |
        helm upgrade --install todo-app ./charts/todo-app \
          -f charts/todo-app/values-prod.yaml \
          --set image.tag=${{ needs.build.outputs.version }} \
          --namespace todo-prod \
          --create-namespace \
          --atomic \
          --timeout 15m \
          --wait-for-jobs
    - name: Smoke tests
      run: |
        pytest tests/smoke/ -v --prod
    - name: Notify success
      uses: slackapi/slack-github-action@v1
      with:
        payload: |
          {
            "text": "✅ Production deployment successful: ${{ needs.build.outputs.version }}"
          }
```

### Monitoring and Logging Stack

#### Prometheus Configuration
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-backend-monitor
  namespace: todo-prod
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
  namespaceSelector:
    matchNames:
    - todo-prod
```

#### Grafana Dashboard Panels
- **Service Overview**: Request rate, error rate, latency (P50/P95/P99)
- **Kafka Metrics**: Consumer lag, producer throughput, topic partition health
- **Dapr Metrics**: Sidecar CPU/memory, pub/sub latency, state store operations
- **Business Metrics**: Tasks created/completed, active users, search queries
- **Resource Metrics**: CPU/memory usage, pod count, HPA status

#### Alert Rules
```yaml
groups:
- name: todo-alerts
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  - alert: HighLatency
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "P95 latency is {{ $value | humanizeDuration }}"
  
  - alert: KafkaConsumerLag
    expr: kafka_consumer_group_lag > 1000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Kafka consumer lag high"
      description: "Consumer lag is {{ $value }}"
  
  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Pod crash looping"
      description: "Pod {{ $labels.pod }} is crash looping"
```

#### Logging Stack (Loki + Fluent Bit)
```yaml
# Fluent Bit Configuration
[SERVICE]
    Flush         5
    Grace         30
    Log_Level     info

[INPUT]
    Name          tail
    Path          /var/log/containers/*.log
    Parser        docker
    Tag           kube.*
    Refresh_Interval 10

[FILTER]
    Name          kubernetes
    Match         kube.*
    Kube_URL      https://kubernetes.default.svc:443
    Merge_Log     On
    Keep_Log      Off

[OUTPUT]
    Name          loki
    Match         *
    Host          loki.todo-prod.svc.cluster.local
    Port          3100
    Labels        job=fluentbit
```

---

## Acceptance Criteria

### Phase V Must Have (P0)

#### Advanced Features
- [ ] Recurring tasks with RRULE support (daily, weekly, monthly, yearly, custom)
- [ ] Due dates with timezone support
- [ ] Reminders (email, push, in-app) with configurable offsets
- [ ] Priority levels (low, medium, high, urgent)
- [ ] Multi-tag support per task
- [ ] Full-text search (title, description, tags)
- [ ] Filter by status, priority, tags, due date, date range
- [ ] Search latency <100ms (P95)
- [ ] Filter latency <50ms (P95)

#### Event-Driven Architecture
- [ ] All features publish/consume Kafka events
- [ ] Event schemas documented and versioned
- [ ] Dead letter queue handles failures
- [ ] Event ordering guaranteed per task (partition key)
- [ ] Schema registry implemented

#### Dapr Jobs API
- [ ] Cron binding configured for recurring tasks
- [ ] Scheduled jobs for reminders
- [ ] Overdue detection via scheduled jobs
- [ ] Job execution logged and monitored

#### Cloud Kubernetes (AKS/GKE)
- [ ] AKS or GKE cluster provisioned (Terraform)
- [ ] Managed Redis (Azure Cache / Memorystore)
- [ ] Managed Kafka (Confluent Cloud)
- [ ] Managed secrets (Key Vault / Secret Manager)
- [ ] Ingress with TLS (cert-manager)
- [ ] Cloud monitoring integrated
- [ ] Migration from Minikube tested

#### CI/CD Pipeline
- [ ] Multi-environment pipeline (dev → staging → prod)
- [ ] Manual approval for production
- [ ] Integration tests in staging
- [ ] Smoke tests in production
- [ ] Rollback capability
- [ ] Slack notifications

#### Monitoring and Logging
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards (service + business metrics)
- [ ] Jaeger distributed tracing
- [ ] Loki log aggregation
- [ ] Alert rules configured (error rate, latency, consumer lag)
- [ ] PagerDuty integration
- [ ] Runbooks documented

---

## Testing Requirements

### Unit Tests
| Component | Coverage Target |
|-----------|-----------------|
| Backend API | 90% |
| Recurring Task Logic | 95% |
| Reminder Service | 95% |
| Search Service | 90% |
| Event Handlers | 95% |

### Integration Tests
- [ ] Recurring task instance generation
- [ ] Reminder trigger and notification
- [ ] Search indexing and query
- [ ] Filter combinations
- [ ] Kafka event flow (all event types)
- [ ] Dapr Jobs execution

### Performance Tests
- [ ] Load test: 1000 concurrent users
- [ ] Search latency: <100ms (P95)
- [ ] Filter latency: <50ms (P95)
- [ ] Event throughput: >1000 events/sec
- [ ] Kafka consumer lag under load

### Migration Tests
- [ ] Minikube → AKS migration
- [ ] Minikube → GKE migration
- [ ] Data migration (Redis → Managed Redis)
- [ ] DNS cutover
- [ ] Rollback procedure

---

## Security Requirements

### Cloud Security
- [ ] Private cluster (no public API endpoint)
- [ ] Network policies enforced
- [ ] Pod security standards (restricted)
- [ ] Workload identity (no long-lived credentials)
- [ ] Encryption at rest (database, logs)
- [ ] Encryption in transit (mTLS via Dapr)

### Compliance
- [ ] GDPR compliance (data retention, deletion)
- [ ] Audit logging enabled
- [ ] Access logging (who accessed what)
- [ ] Data residency support

---

## Observability Requirements

### Metrics
- [ ] RED metrics (Rate, Errors, Duration) per service
- [ ] USE metrics (Utilization, Saturation, Errors) per resource
- [ ] Business metrics (tasks created, completed, active users)
- [ ] Kafka metrics (lag, throughput, partition health)
- [ ] Dapr metrics (sidecar health, pub/sub latency)

### Logging
- [ ] Structured JSON logs
- [ ] Correlation ID across services
- [ ] Log levels (DEBUG, INFO, WARN, ERROR)
- [ ] Log aggregation (Fluent Bit → Loki)
- [ ] Log retention: 30 days

### Tracing
- [ ] Distributed tracing (Jaeger)
- [ ] Trace sampling: 10% production, 100% staging
- [ ] Trace ID in logs
- [ ] Cross-service trace propagation

### Alerting
- [ ] Critical alerts (PagerDuty)
- [ ] Warning alerts (Slack)
- [ ] Info alerts (email digest)
- [ ] Alert routing by service
- [ ] On-call rotation configured

---

## Resource Requirements

### AKS Cluster
```
Node Pool: Standard_DS2_v2
Node Count: 3 (system) + 3-10 (user, autoscaling)
Estimated Cost: ~$300/month
```

### GKE Cluster
```
Node Pool: e2-standard-2
Node Count: 3 (min) - 10 (max)
Estimated Cost: ~$250/month
```

### Managed Services
| Service | AKS | GKE |
|---------|-----|-----|
| Redis | Azure Cache (2GB) | Memorystore (2GB) |
| Kafka | Confluent Cloud (Basic) | Confluent Cloud (Basic) |
| Secrets | Key Vault | Secret Manager |
| Monitoring | Azure Monitor | Cloud Monitoring |

**Total Estimated Monthly Cost**: $500-800 (production)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | Uptime monitoring |
| P95 Latency | <300ms | API metrics |
| Search Latency | <100ms | Search service metrics |
| Event Throughput | 1000+ events/sec | Kafka metrics |
| Consumer Lag | <100 | Kafka consumer lag |
| Deployment Frequency | Daily | CI/CD metrics |
| Change Failure Rate | <5% | Deployment success rate |
| Mean Time to Recovery | <5 min | Incident metrics |

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cloud cost overrun | High | Medium | Resource limits, autoscaling, cost monitoring |
| Kafka partition issues | High | Low | Proper partition key design, monitoring |
| Recurring task edge cases | Medium | Medium | Comprehensive testing, manual override |
| Timezone bugs | Medium | Medium | UTC storage, timezone conversion library |
| Search relevance | Medium | Low | Tuning, user feedback loop |
| Migration downtime | High | Low | Blue-green deployment, rollback plan |

---

## References

- **Phase IV Spec**: `specs/features/phase-iv-local-kubernetes.md`
- **Constitution**: `.specify/memory/phase-iv-v-constitution.md`
- **Dapr Jobs API**: https://docs.dapr.io/developing-applications/building-blocks/bindings/bindings-overview/
- **RRULE Spec**: https://datatracker.ietf.org/doc/html/rfc5545
- **Confluent Cloud**: https://www.confluent.io/confluent-cloud/
- **Azure AKS**: https://docs.microsoft.com/azure/aks/
- **Google GKE**: https://cloud.google.com/kubernetes-engine

---

**Version**: 1.0.0  
**Created**: 2026-03-12  
**Author**: AI Assistant (Spec-Driven Development)  
**Status**: Draft - Awaiting User Approval  
**Next**: Architecture Plan (`phase-v-plan.md`) → Implementation Tasks (`phase-v-tasks.md`)
