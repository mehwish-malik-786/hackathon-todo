# Phase V: Implementation Tasks

## Document Information

**Phase**: Phase V (Advanced Cloud Deployment)  
**Version**: 1.0.0  
**Created**: 2026-03-12  
**Status**: Ready for Implementation  
**Constitution**: `.specify/memory/phase-iv-v-constitution.md`  
**Specification**: `specs/features/phase-v-advanced-cloud.md`  
**Architecture Plan**: `specs/features/phase-v-plan.md`  
**Prerequisite**: Phase IV completion (`phase-iv-tasks.md`)

---

## Task Summary

| Category | Task Count | Priority Breakdown |
|----------|-----------|-------------------|
| Advanced Features | 6 | P0: 6 |
| Event Streaming | 4 | P0: 4 |
| Search & Filter | 3 | P0: 3 |
| Cloud Infrastructure | 5 | P0: 5 |
| Dapr Jobs | 2 | P0: 2 |
| Managed Services | 3 | P0: 3 |
| Production CI/CD | 3 | P0: 3 |
| Monitoring & Alerting | 3 | P0: 3 |
| Security & Compliance | 3 | P0: 3 |
| Migration | 3 | P0: 3 |
| Testing | 4 | P0: 4 |
| Documentation | 2 | P1: 2 |
| **Total** | **44** | **P0: 42, P1: 2** |

---

## Advanced Features Tasks

### PH5-FEATURE-001: Implement Recurring Tasks

**Task ID**: PH5-FEATURE-001  
**Priority**: P0  
**Estimated Hours**: 6

**Description**: Implement recurring task functionality with RRULE support (daily, weekly, monthly, yearly, custom patterns) including next occurrence calculation and instance creation.

**Preconditions**:
- Phase IV completed (all PH4-* tasks)
- Backend API deployed and functional
- Dapr state store configured
- Kafka event streaming functional

**Expected Output**:
- RRULE parsing library integrated
- Recurrence metadata stored with tasks
- Next occurrence calculation implemented
- Recurring task instance creation automated
- Event schema extended with recurrence field
- API endpoints for recurring task management

**Files to Create**:
- `backend/services/recurrence_service.py` - Recurrence logic
- `backend/models/recurrence.py` - Recurrence data model
- `backend/api/recurrence.py` - Recurrence API endpoints
- `tests/test_recurrence.py` - Recurrence tests

**Files to Modify**:
- `backend/models/task.py` - Add recurrence field
- `backend/schemas/task.py` - Add recurrence schema
- `k8s/dapr-components/binding-cron.yaml` - Cron binding for recurrence checking

**Related Spec Sections**:
- Section: Requirements → FR-V-001 (Recurring Tasks)
- Section: Event Schema Definitions → task.created (with recurrence)
- Section: Technical Specifications → Dapr Jobs API Configuration

**Acceptance Criteria**:
- [ ] Task can be created with RRULE pattern (FREQ=WEEKLY;BYDAY=MO)
- [ ] Next occurrence calculated correctly
- [ ] Recurring instance created automatically at scheduled time
- [ ] Event includes recurrence metadata
- [ ] API supports GET/PUT/DELETE for recurrence settings
- [ ] Timezone support implemented

---

### PH5-FEATURE-002: Implement Due Dates and Timezones

**Task ID**: PH5-FEATURE-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Implement due date functionality with timezone support, allowing users to set task due dates in their local timezone with automatic UTC conversion.

**Preconditions**:
- PH5-FEATURE-001 completed (Recurring tasks implemented)
- Backend API deployed
- Database schema supports due date fields

**Expected Output**:
- Due date field added to task model
- Timezone support with IANA timezone database
- UTC storage with timezone conversion
- Overdue detection logic
- API endpoints for due date management

**Files to Create**:
- `backend/services/due_date_service.py` - Due date logic
- `backend/utils/timezone.py` - Timezone utilities

**Files to Modify**:
- `backend/models/task.py` - Add due_date, timezone fields
- `backend/schemas/task.py` - Add due_date schema
- `backend/api/tasks.py` - Add due date endpoints

**Related Spec Sections**:
- Section: Requirements → FR-V-002 (Due Dates)
- Section: Event Schema Definitions → task.created (with due date)

**Acceptance Criteria**:
- [ ] Task can be created with due date
- [ ] Timezone stored with task (e.g., "America/New_York")
- [ ] Due date converted to UTC for storage
- [ ] Overdue detection works correctly
- [ ] API supports due date filtering

---

### PH5-FEATURE-003: Implement Reminders

**Task ID**: PH5-FEATURE-003  
**Priority**: P0  
**Estimated Hours**: 6

**Description**: Implement configurable reminder system with email, push, and in-app notifications triggered before task due dates.

**Preconditions**:
- PH5-FEATURE-002 completed (Due dates implemented)
- Dapr Cron binding configured
- Email service credentials available (SendGrid/SES)
- Push notification service configured (FCM/APNs)

**Expected Output**:
- Reminder configuration stored with tasks
- Dapr Cron triggers reminder processor
- Email reminders sent via SendGrid/SES
- Push notifications sent via FCM/APNs
- In-app notifications stored
- Reminder delivery tracking

**Files to Create**:
- `backend/services/reminder_service.py` - Reminder logic
- `backend/services/email_service.py` - Email integration
- `backend/services/push_service.py` - Push notification integration
- `backend/api/reminders.py` - Reminder API endpoints
- `k8s/dapr-components/binding-reminder-cron.yaml` - Reminder cron binding

**Files to Modify**:
- `backend/models/task.py` - Add reminders field
- `backend/schemas/task.py` - Add reminder schema
- `k8s/jobs/reminder-processor-job.yaml` - Reminder processor deployment

**Related Spec Sections**:
- Section: Requirements → FR-V-003 (Reminders)
- Section: Event Schema Definitions → task.reminder.triggered
- Section: Technical Specifications → Dapr Jobs API

**Acceptance Criteria**:
- [ ] Task can have multiple reminders with offsets (1d, 1h before)
- [ ] Email reminders sent at configured times
- [ ] Push notifications sent at configured times
- [ ] Reminder delivery tracked and logged
- [ ] Failed reminders retried
- [ ] API supports reminder CRUD operations

---

### PH5-FEATURE-004: Implement Priority Levels

**Task ID**: PH5-FEATURE-004  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Implement task priority levels (Low, Medium, High, Urgent) with filtering and sorting capabilities.

**Preconditions**:
- Phase IV completed
- Backend API deployed

**Expected Output**:
- Priority enum defined (low, medium, high, urgent)
- Priority field added to task model
- API supports priority filtering
- UI can sort by priority
- Priority changes tracked in events

**Files to Create**:
- `backend/models/priority.py` - Priority enum
- `tests/test_priority.py` - Priority tests

**Files to Modify**:
- `backend/models/task.py` - Add priority field
- `backend/schemas/task.py` - Add priority schema
- `backend/api/tasks.py` - Add priority filtering
- `backend/events/task_events.py` - Track priority changes

**Related Spec Sections**:
- Section: Requirements → FR-V-004 (Priority Levels)
- Section: Event Schema Definitions → task.updated (with priority changes)

**Acceptance Criteria**:
- [ ] Task can be created with priority (default: medium)
- [ ] Priority can be updated
- [ ] API supports filter by priority
- [ ] API supports sort by priority
- [ ] Priority changes tracked in event schema

---

### PH5-FEATURE-005: Implement Tags

**Task ID**: PH5-FEATURE-005  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Implement multi-tag support for task organization with tag creation, assignment, and filtering capabilities.

**Preconditions**:
- Phase IV completed
- Backend API deployed

**Expected Output**:
- Tags field added to task model (array of strings)
- Tag validation (max length, allowed characters)
- API endpoints for tag management
- Tag-based filtering implemented
- Tag suggestions based on usage

**Files to Create**:
- `backend/services/tag_service.py` - Tag management
- `backend/api/tags.py` - Tag API endpoints

**Files to Modify**:
- `backend/models/task.py` - Add tags field
- `backend/schemas/task.py` - Add tags schema
- `backend/api/tasks.py` - Add tag filtering

**Related Spec Sections**:
- Section: Requirements → FR-V-005 (Tags)
- Section: Event Schema Definitions → task.created (with tags)

**Acceptance Criteria**:
- [ ] Task can have multiple tags
- [ ] Tags validated (max 50 chars, alphanumeric + dash)
- [ ] API supports filter by tags (AND/OR logic)
- [ ] Tag suggestions returned based on usage
- [ ] Tags indexed for fast filtering

---

### PH5-FEATURE-006: Implement Search and Filter

**Task ID**: PH5-FEATURE-006  
**Priority**: P0  
**Estimated Hours**: 8

**Description**: Implement full-text search across tasks (title, description, tags) with advanced filtering by status, priority, tags, due date, and date range.

**Preconditions**:
- PH5-FEATURE-004 completed (Priority implemented)
- PH5-FEATURE-005 completed (Tags implemented)
- Elasticsearch cluster available (Phase V cloud)

**Expected Output**:
- Elasticsearch integration for search
- Full-text search across title, description, tags
- Advanced filtering (status, priority, tags, due date, date range)
- Search results ranked by relevance
- Search latency < 100ms (P95)
- Search indexing via Kafka events

**Files to Create**:
- `backend/services/search_service.py` - Search logic
- `backend/services/indexing_service.py` - Elasticsearch indexing
- `backend/api/search.py` - Search API endpoints
- `backend/events/search_indexer.py` - Event-driven indexing
- `k8s/services/search-indexer-deployment.yaml` - Search indexer service

**Files to Modify**:
- `backend/main.py` - Add search routes
- `k8s/dapr-components/pubsub-kafka.yaml` - Add search topic

**Related Spec Sections**:
- Section: Requirements → FR-V-006 (Search), FR-V-007 (Filter)
- Section: Event Schema Definitions → task.searched, task.search.index
- Section: Technical Specifications → Elasticsearch Scaling Strategy

**Acceptance Criteria**:
- [ ] Full-text search returns relevant results
- [ ] Search latency < 100ms (P95)
- [ ] Filter by status works
- [ ] Filter by priority works
- [ ] Filter by tags works (multi-tag support)
- [ ] Filter by due date range works
- [ ] Combined filters work correctly
- [ ] Search results highlight matched terms

---

## Event Streaming Tasks

### PH5-EVENT-001: Extend Event Schemas

**Task ID**: PH5-EVENT-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Extend CloudEvents schemas to include Phase V features (recurrence, due date, reminders, priority, tags) with proper versioning.

**Preconditions**:
- Phase IV completed (Base event schemas exist)
- PH5-FEATURE-001 to PH5-FEATURE-006 completed or in progress

**Expected Output**:
- Extended event schemas for all Phase V features
- Schema versioning (v1.0 → v2.0)
- Backward compatibility maintained
- Schema documentation updated
- Schema registry configured (Confluent Schema Registry)

**Files to Create**:
- `backend/schemas/events_v2.py` - Extended event schemas
- `docs/schemas/event-schemas-v2.md` - Schema documentation

**Files to Modify**:
- `backend/events/task_events.py` - Update to use v2 schemas
- `backend/events/event_publisher.py` - Add schema versioning

**Related Spec Sections**:
- Section: Event Schema Definitions (all Phase V schemas)
- Section: Technical Specifications → Event Schema

**Acceptance Criteria**:
- [ ] task.created schema includes recurrence, due_date, reminders, priority, tags
- [ ] task.updated schema includes field-level changes tracking
- [ ] task.reminder.triggered schema defined
- [ ] task.searched schema defined
- [ ] task.search.index schema defined
- [ ] Schema registry validates events
- [ ] Backward compatibility with v1 schemas

---

### PH5-EVENT-002: Create Additional Kafka Topics

**Task ID**: PH5-EVENT-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Create additional Kafka topics for Phase V features with appropriate partitions and retention policies.

**Preconditions**:
- Phase IV completed (Kafka topics created)
- PH5-EVENT-001 completed (Event schemas extended)

**Expected Output**:
- Topic `todo.tasks.recurrence` created (3 partitions, 30d retention)
- Topic `todo.search` created (3 partitions, 7d retention)
- Topic `todo.notifications` created (6 partitions, 30d retention)
- Topic `todo.audit` created (3 partitions, 90d retention)
- Topics configured via Kubernetes Job

**Files to Create**:
- `k8s/jobs/kafka-topics-phase-v-job.yaml` - Phase V topics creation job

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Kafka Topic Definitions (Phase V)
- Section: Event-Driven Architecture

**Acceptance Criteria**:
- [ ] All 4 new topics created
- [ ] Partition counts match specification
- [ ] Retention policies configured correctly
- [ ] Topics verified via Kafka CLI

---

### PH5-EVENT-003: Implement Event Processor for Phase V

**Task ID**: PH5-EVENT-003  
**Priority**: P0  
**Estimated Hours**: 6

**Description**: Implement event processor service extensions for Phase V features including recurrence processing, reminder triggering, and search indexing.

**Preconditions**:
- PH5-EVENT-001 completed (Event schemas extended)
- PH5-EVENT-002 completed (Kafka topics created)
- Phase IV event processor deployed

**Expected Output**:
- Recurrence event processor implemented
- Reminder event processor implemented
- Search indexing event processor implemented
- Event processors scale independently
- Dead letter queue handling for failed events

**Files to Create**:
- `backend/events/recurrence_processor.py` - Recurrence event processing
- `backend/events/reminder_processor.py` - Reminder event processing
- `backend/events/search_indexer.py` - Search indexing
- `k8s/services/recurrence-processor-deployment.yaml`
- `k8s/services/reminder-processor-deployment.yaml`
- `k8s/services/search-indexer-deployment.yaml`

**Files to Modify**:
- `backend/events/event_consumer.py` - Add Phase V event handlers

**Related Spec Sections**:
- Section: Event Flow Architecture (Phase V)
- Section: Technical Specifications → Event Processing Tier

**Acceptance Criteria**:
- [ ] Recurrence events processed and instances created
- [ ] Reminder events trigger notifications
- [ ] Search events update Elasticsearch index
- [ ] Failed events routed to dead letter queue
- [ ] Event processors scale based on Kafka lag

---

### PH5-EVENT-004: Configure Dead Letter Queue Handling

**Task ID**: PH5-EVENT-004  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure dead letter queue monitoring and retry mechanisms for failed event processing.

**Preconditions**:
- PH5-EVENT-003 completed (Event processors implemented)
- Kafka dead letter topic configured

**Expected Output**:
- DLQ monitoring dashboard created
- Automatic retry logic with exponential backoff
- Manual replay capability for DLQ events
- Alerting on DLQ message count threshold

**Files to Create**:
- `backend/services/dlq_service.py` - DLQ handling
- `k8s/jobs/dlq-replay-job.yaml` - DLQ replay job
- `grafana/dashboards/dlq-monitoring.json` - DLQ dashboard

**Files to Modify**:
- `backend/events/event_consumer.py` - Add DLQ routing

**Related Spec Sections**:
- Section: Failover Handling
- Section: Technical Specifications → Kafka Topic Definitions

**Acceptance Criteria**:
- [ ] Failed events routed to todo.dead-letter topic
- [ ] DLQ monitoring dashboard shows message count
- [ ] Alert triggers when DLQ count > 100
- [ ] Manual replay job can reprocess DLQ events
- [ ] Retry logic implements exponential backoff (3 attempts)

---

## Search & Filter Tasks

### PH5-SEARCH-001: Deploy Elasticsearch Cluster

**Task ID**: PH5-SEARCH-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Deploy Elasticsearch cluster for full-text search either via Helm (Minikube) or managed service (cloud).

**Preconditions**:
- Phase IV completed
- Helm 3.x installed
- Sufficient cluster resources (4GB RAM minimum for ES)

**Expected Output**:
- Elasticsearch deployed (single node for dev, multi-node for prod)
- Kibana deployed for index management
- Index templates configured for tasks
- Elasticsearch accessible within cluster

**Files to Create**:
- `k8s/search/elasticsearch-values.yaml` - ES Helm values
- `k8s/search/elasticsearch-index-template.yaml` - Index template

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Elasticsearch Scaling Strategy
- Section: Requirements → FR-V-006 (Search)

**Acceptance Criteria**:
- [ ] `kubectl get pods -l app.kubernetes.io/name=elasticsearch` shows Running
- [ ] Elasticsearch accessible at elasticsearch:9200
- [ ] Index template created for tasks index
- [ ] Kibana accessible for index management

---

### PH5-SEARCH-002: Implement Search Indexing

**Task ID**: PH5-SEARCH-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Implement search indexing service that consumes Kafka events and updates Elasticsearch index in real-time.

**Preconditions**:
- PH5-SEARCH-001 completed (Elasticsearch deployed)
- PH5-EVENT-002 completed (Search topic created)

**Expected Output**:
- Search indexer service deployed
- Real-time indexing from Kafka events
- Index mapping configured for full-text search
- Bulk indexing for initial data load

**Files to Create**:
- `backend/services/search_indexer.py` - Search indexing logic
- `k8s/services/search-indexer-deployment.yaml` - Indexer deployment

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Event Flow Architecture → Event Flow: Search Indexing
- Section: Technical Specifications → Elasticsearch

**Acceptance Criteria**:
- [ ] task.created event triggers index creation
- [ ] task.updated event triggers index update
- [ ] task.deleted event triggers index deletion
- [ ] Index mapping supports full-text search
- [ ] Initial bulk indexing completes successfully

---

### PH5-SEARCH-003: Implement Search API

**Task ID**: PH5-SEARCH-003  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Implement search API endpoints with query parsing, filtering, ranking, and result highlighting.

**Preconditions**:
- PH5-SEARCH-002 completed (Search indexing implemented)
- Elasticsearch cluster operational

**Expected Output**:
- Search API endpoint: GET /api/search
- Query parsing with support for operators (AND, OR, NOT)
- Result ranking by relevance score
- Highlighting of matched terms
- Pagination support
- Search latency < 100ms (P95)

**Files to Create**:
- `backend/api/search.py` - Search API endpoints
- `backend/services/search_query_builder.py` - Query builder

**Files to Modify**:
- `backend/main.py` - Add search routes

**Related Spec Sections**:
- Section: Requirements → FR-V-006 (Search)
- Section: Event Schema Definitions → task.searched

**Acceptance Criteria**:
- [ ] GET /api/search?q=query returns results
- [ ] Query operators work (AND, OR, NOT)
- [ ] Results ranked by relevance score
- [ ] Matched terms highlighted in results
- [ ] Pagination works (page, page_size)
- [ ] P95 latency < 100ms under load

---

## Cloud Infrastructure Tasks

### PH5-CLOUD-001: Provision AKS Cluster

**Task ID**: PH5-CLOUD-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Provision Azure Kubernetes Service (AKS) cluster with Terraform including node pools, networking, and monitoring integration.

**Preconditions**:
- Phase IV completed
- Azure subscription active
- Terraform installed
- Azure CLI installed and authenticated

**Expected Output**:
- AKS cluster provisioned in East US region
- System node pool: 3 nodes (Standard_DS2_v2)
- User node pool: 3-10 nodes (autoscaling)
- Azure Monitor integration enabled
- Application Gateway Ingress Controller (AGIC) enabled
- Cluster accessible via kubectl

**Files to Create**:
- `terraform/azure/main.tf` - AKS Terraform configuration
- `terraform/azure/variables.tf` - Terraform variables
- `terraform/azure/outputs.tf` - Terraform outputs
- `terraform/azure/.terraform.lock.hcl` - Provider lock file

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Cloud Kubernetes Deployment (AKS)
- Section: Requirements → FR-V-010 (Cloud Kubernetes)

**Acceptance Criteria**:
- [ ] `terraform apply` succeeds
- [ ] AKS cluster created in Azure portal
- [ ] `kubectl get nodes` shows 6 nodes (3 system + 3 user)
- [ ] Azure Monitor integration enabled
- [ ] AGIC addon enabled
- [ ] kubectl context configured

---

### PH5-CLOUD-002: Provision Managed Redis

**Task ID**: PH5-CLOUD-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Provision Azure Cache for Redis (managed service) and configure Dapr state store component for cloud deployment.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Azure subscription active

**Expected Output**:
- Azure Cache for Redis provisioned (Premium tier, 2GB)
- Redis accessible from AKS cluster
- Dapr state store component updated for managed Redis
- Connection secured with TLS and authentication

**Files to Create**:
- `terraform/azure/redis.tf` - Redis Terraform configuration
- `k8s/dapr-components/state-redis-cloud.yaml` - Cloud Dapr state component

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Update Redis host

**Related Spec Sections**:
- Section: Technical Specifications → Cloud Kubernetes Deployment (AKS)
- Section: Migration Strategy → Configuration Changes Matrix

**Acceptance Criteria**:
- [ ] Azure Cache for Redis created in Azure portal
- [ ] Redis accessible from AKS cluster (test connection)
- [ ] Dapr component configured with managed Redis
- [ ] TLS enabled for Redis connection
- [ ] Authentication via secret reference

---

### PH5-CLOUD-003: Configure Confluent Cloud Kafka

**Task ID**: PH5-CLOUD-003  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Configure Confluent Cloud Kafka cluster and update Dapr pub/sub component for managed Kafka service.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Confluent Cloud account active

**Expected Output**:
- Confluent Cloud Kafka cluster provisioned (Basic tier)
- Topics created (todo.tasks, todo.chat, todo.reminders, etc.)
- SASL authentication configured
- Dapr pub/sub component updated for Confluent Cloud
- Topics configured with appropriate partitions

**Files to Create**:
- `k8s/dapr-components/pubsub-kafka-cloud.yaml` - Cloud Dapr pub/sub component
- `scripts/confluent-create-topics.sh` - Topic creation script

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Update Kafka brokers

**Related Spec Sections**:
- Section: Technical Specifications → Cloud Kubernetes Deployment (AKS)
- Section: Migration Strategy → Configuration Changes Matrix

**Acceptance Criteria**:
- [ ] Confluent Cloud Kafka cluster created
- [ ] All topics created with correct partitions
- [ ] SASL authentication works
- [ ] Dapr component configured for Confluent Cloud
- [ ] SSL/TLS enabled for Kafka connection
- [ ] Test publish/consume succeeds

---

### PH5-CLOUD-004: Configure Azure Key Vault Integration

**Task ID**: PH5-CLOUD-004  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Azure Key Vault for secrets management and integrate with Dapr secret store component.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Azure Key Vault created
- Azure CLI authenticated

**Expected Output**:
- Azure Key Vault provisioned
- Secrets stored in Key Vault (Redis password, Kafka credentials, etc.)
- Dapr secret store component configured for Azure Key Vault
- AKS cluster has managed identity for Key Vault access
- CSI driver for Key Vault installed

**Files to Create**:
- `terraform/azure/keyvault.tf` - Key Vault Terraform configuration
- `k8s/dapr-components/secret-keyvault.yaml` - Dapr Key Vault component
- `k8s/security/azure-workload-identity.yaml` - Workload identity configuration

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Enable Key Vault integration

**Related Spec Sections**:
- Section: Secrets Management → Azure Key Vault Integration
- Section: Security Requirements → Secrets Security

**Acceptance Criteria**:
- [ ] Azure Key Vault created
- [ ] Secrets stored in Key Vault
- [ ] Dapr component configured for Key Vault
- [ ] AKS cluster can access Key Vault via managed identity
- [ ] `curl http://localhost:3500/v1.0/secrets/azure-keyvault/secret-name` returns secret

---

### PH5-CLOUD-005: Configure Cloud Ingress with TLS

**Task ID**: PH5-CLOUD-005  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Configure Application Gateway Ingress Controller (AGIC) with TLS termination and custom domain for AKS deployment.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Custom domain available
- DNS management access

**Expected Output**:
- Application Gateway Ingress Controller configured
- TLS certificate provisioned (Let's Encrypt via cert-manager)
- Ingress configured with custom domain (todo.example.com)
- DNS records updated to point to Application Gateway
- HTTPS redirect configured

**Files to Create**:
- `k8s/ingress/agic-ingress.yaml` - AGIC ingress configuration
- `k8s/ingress/cert-manager-clusterissuer.yaml` - Let's Encrypt ClusterIssuer
- `k8s/ingress/tls-secret.yaml` - TLS secret (if not using cert-manager)

**Files to Modify**:
- `charts/todo-app/templates/infrastructure/ingress.yaml` - Update for AGIC
- `charts/todo-app/values-aks.yaml` - Add ingress host configuration

**Related Spec Sections**:
- Section: Kubernetes Services and Ingress (Phase V)
- Section: Technical Specifications → Cloud Ingress Architecture (AKS)

**Acceptance Criteria**:
- [ ] Application Gateway created in Azure
- [ ] Ingress accessible via custom domain
- [ ] TLS certificate valid (Let's Encrypt)
- [ ] HTTPS redirect works
- [ ] DNS resolves to Application Gateway IP
- [ ] `curl https://todo.example.com` returns 200

---

## Dapr Jobs Tasks

### PH5-DAPRJOB-001: Configure Dapr Cron Binding for Recurring Tasks

**Task ID**: PH5-DAPRJOB-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Dapr Cron binding component for recurring task processing with configurable schedule.

**Preconditions**:
- Phase IV completed (Dapr runtime installed)
- PH5-FEATURE-001 completed (Recurring tasks implemented)

**Expected Output**:
- Dapr Cron binding component created
- Schedule configured (every 5 minutes for recurring check)
- Recurring processor service subscribes to Cron binding
- Recurring task instances created automatically

**Files to Create**:
- `k8s/dapr-components/binding-recurring-cron.yaml` - Recurring Cron binding

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Dapr Jobs API Configuration
- Section: Event Flow Architecture → Event Flow: Recurring Task Creation

**Acceptance Criteria**:
- [ ] Dapr Cron component deployed
- [ ] Schedule set to every 5 minutes
- [ ] Recurring processor receives Cron triggers
- [ ] Recurring task instances created at scheduled times
- [ ] Cron binding can be disabled via values.yaml

---

### PH5-DAPRJOB-002: Configure Dapr Cron Binding for Reminders

**Task ID**: PH5-DAPRJOB-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Dapr Cron binding component for reminder processing with every-minute schedule for accurate reminder delivery.

**Preconditions**:
- PH5-FEATURE-003 completed (Reminders implemented)
- Phase IV completed (Dapr runtime installed)

**Expected Output**:
- Dapr Cron binding component created for reminders
- Schedule configured (every 1 minute for reminder check)
- Reminder processor service subscribes to Cron binding
- Reminders delivered at configured times

**Files to Create**:
- `k8s/dapr-components/binding-reminder-cron.yaml` - Reminder Cron binding

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Technical Specifications → Dapr Jobs API Configuration
- Section: Event Flow Architecture → Event Flow: Reminder Trigger

**Acceptance Criteria**:
- [ ] Dapr Cron component deployed for reminders
- [ ] Schedule set to every 1 minute
- [ ] Reminder processor receives Cron triggers
- [ ] Reminders delivered at configured offsets before due date
- [ ] Cron binding can be disabled via values.yaml

---

## Managed Services Tasks

### PH5-MANAGED-001: Configure Azure Monitor Integration

**Task ID**: PH5-MANAGED-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Configure Azure Monitor (managed Prometheus) for metrics collection and replace self-hosted Prometheus stack.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Azure Monitor workspace created

**Expected Output**:
- Azure Monitor managed Prometheus configured
- Azure Monitor Agent installed on AKS nodes
- Self-hosted Prometheus decommissioned
- Grafana configured to use Azure Monitor data source
- Metrics scraped from all services

**Files to Create**:
- `terraform/azure/monitor.tf` - Azure Monitor Terraform
- `k8s/observability/azure-monitor-agent.yaml` - AMA configuration

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Enable Azure Monitor, disable Prometheus

**Related Spec Sections**:
- Section: Monitoring and Observability (Phase V)
- Section: Technical Specifications → Azure Monitor Integration

**Acceptance Criteria**:
- [ ] Azure Monitor workspace created
- [ ] Azure Monitor Agent running on all nodes
- [ ] Metrics visible in Azure Portal
- [ ] Grafana connected to Azure Monitor datasource
- [ ] Self-hosted Prometheus decommissioned

---

### PH5-MANAGED-002: Configure Azure Log Analytics

**Task ID**: PH5-MANAGED-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Azure Log Analytics for centralized log aggregation and replace self-hosted Loki stack.

**Preconditions**:
- PH5-MANAGED-001 completed (Azure Monitor configured)
- Log Analytics workspace created

**Expected Output**:
- Azure Log Analytics workspace configured
- Fluent Bit configured to send logs to Log Analytics
- Self-hosted Loki decommissioned
- Logs searchable in Azure Portal
- Log queries via Kusto Query Language (KQL)

**Files to Create**:
- `k8s/observability/fluent-bit-azure.yaml` - Fluent Bit Azure configuration

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Enable Log Analytics, disable Loki

**Related Spec Sections**:
- Section: Observability Requirements → Logging
- Section: Monitoring and Observability (Phase V)

**Acceptance Criteria**:
- [ ] Log Analytics workspace created
- [ ] Fluent Bit sending logs to Log Analytics
- [ ] Logs searchable in Azure Portal
- [ ] KQL queries work correctly
- [ ] Self-hosted Loki decommissioned

---

### PH5-MANAGED-003: Configure Managed Grafana

**Task ID**: PH5-MANAGED-003  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Azure Managed Grafana for dashboards and alerting with Azure Monitor and Log Analytics integration.

**Preconditions**:
- PH5-MANAGED-001 completed (Azure Monitor configured)
- PH5-MANAGED-002 completed (Log Analytics configured)

**Expected Output**:
- Azure Managed Grafana provisioned
- Azure Monitor datasource configured
- Log Analytics datasource configured
- Dashboards imported/created
- Alerting rules configured

**Files to Create**:
- `terraform/azure/grafana.tf` - Managed Grafana Terraform
- `grafana/dashboards/phase-v-system.json` - System dashboard
- `grafana/dashboards/phase-v-business.json` - Business metrics dashboard

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Monitoring and Observability (Phase V)
- Section: Observability Requirements → Metrics

**Acceptance Criteria**:
- [ ] Azure Managed Grafana provisioned
- [ ] Azure Monitor datasource connected
- [ ] Log Analytics datasource connected
- [ ] System dashboard shows all services
- [ ] Business dashboard shows tasks created/completed
- [ ] Alerting rules configured

---

## Production CI/CD Tasks

### PH5-CICD-001: Configure Multi-Environment Pipeline

**Task ID**: PH5-CICD-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Extend GitHub Actions pipeline for multi-environment deployment (dev → staging → production) with appropriate approval gates.

**Preconditions**:
- PH4-CICD-003 completed (Environment protection configured)
- AKS cluster provisioned

**Expected Output**:
- Development environment: auto-deploy on merge to develop
- Staging environment: auto-deploy on tag with integration tests
- Production environment: manual approval (2 reviewers) + smoke tests
- Environment-specific Helm values used
- Deployment status reported to Slack

**Files to Create**:
- `.github/workflows/ci-cd-phase-v.yaml` - Phase V CI/CD workflow

**Files to Modify**:
- `.github/workflows/ci-cd.yaml` - Update for multi-environment

**Related Spec Sections**:
- Section: CI/CD Flow (Phase V)
- Section: Technical Specifications → Production CI/CD Pipeline

**Acceptance Criteria**:
- [ ] Dev deployment triggers on merge to develop
- [ ] Staging deployment triggers on tag
- [ ] Production requires 2 reviewer approvals
- [ ] Integration tests run in staging
- [ ] Smoke tests run in production
- [ ] Slack notifications sent for all environments

---

### PH5-CICD-002: Configure Blue-Green Deployment

**Task ID**: PH5-CICD-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Implement blue-green deployment strategy for zero-downtime production deployments.

**Preconditions**:
- PH5-CICD-001 completed (Multi-environment pipeline)
- AKS cluster with Application Gateway

**Expected Output**:
- Blue and green environments configured
- Traffic switching via Application Gateway backend pool
- Health checks validate new environment before switch
- Automatic rollback on health check failure
- Deployment history tracked

**Files to Create**:
- `k8s/deployment/blue-green-controller.yaml` - Blue-green controller
- `scripts/blue-green-switch.sh` - Traffic switch script

**Files to Modify**:
- `.github/workflows/ci-cd-phase-v.yaml` - Add blue-green steps

**Related Spec Sections**:
- Section: CI/CD Flow (Phase V)
- Section: Deployment Strategy

**Acceptance Criteria**:
- [ ] Blue and green deployments exist
- [ ] Traffic switches from blue to green on successful deployment
- [ ] Health checks validate green environment
- [ ] Automatic rollback if green health checks fail
- [ ] Zero downtime during deployment

---

### PH5-CICD-003: Configure Automated Rollback

**Task ID**: PH5-CICD-003  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure automated rollback based on health check failures and error rate thresholds.

**Preconditions**:
- PH5-CICD-002 completed (Blue-green deployment)
- Azure Monitor alerting configured

**Expected Output**:
- Rollback triggers on health check failure
- Rollback triggers on error rate > 5%
- Rollback triggers on latency P95 > 1s
- Rollback history tracked
- Notification sent on rollback

**Files to Create**:
- `k8s/monitoring/rollback-alerts.yaml` - Rollback alert rules
- `scripts/automated-rollback.sh` - Rollback script

**Files to Modify**:
- `.github/workflows/ci-cd-phase-v.yaml` - Add rollback logic

**Related Spec Sections**:
- Section: Failover Handling
- Section: CI/CD Flow (Phase V)

**Acceptance Criteria**:
- [ ] Rollback triggers on health check failure
- [ ] Rollback triggers on error rate > 5% for 5 minutes
- [ ] Rollback completes in < 2 minutes
- [ ] Notification sent on rollback
- [ ] Rollback history logged

---

## Monitoring & Alerting Tasks

### PH5-MONITOR-001: Configure Business Metrics Dashboards

**Task ID**: PH5-MONITOR-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create Grafana dashboards for business metrics including tasks created/completed, active users, search queries, and reminder delivery.

**Preconditions**:
- PH5-MANAGED-003 completed (Managed Grafana configured)
- Application emitting business metrics

**Expected Output**:
- Business metrics dashboard created
- Tasks created/completed over time
- Active users (DAU/MAU)
- Search queries count and latency
- Reminder delivery rate
- Recurring task instances created

**Files to Create**:
- `grafana/dashboards/business-metrics.json` - Business dashboard

**Files to Modify**:
- `backend/metrics/business_metrics.py` - Emit business metrics

**Related Spec Sections**:
- Section: Monitoring and Observability (Phase V)
- Section: Observability Requirements → Metrics

**Acceptance Criteria**:
- [ ] Dashboard shows tasks created/completed over time
- [ ] Dashboard shows active users
- [ ] Dashboard shows search query metrics
- [ ] Dashboard shows reminder delivery rate
- [ ] Dashboard auto-refreshes every 5 minutes

---

### PH5-MONITOR-002: Configure Alert Rules

**Task ID**: PH5-MONITOR-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Configure comprehensive alerting rules for infrastructure and business metrics with PagerDuty integration.

**Preconditions**:
- PH5-MANAGED-003 completed (Managed Grafana configured)
- PagerDuty account configured

**Expected Output**:
- Alert rules configured:
  - High error rate (> 1%)
  - High latency (P95 > 500ms)
  - Kafka consumer lag > 1000
  - Pod crash looping
  - Search latency > 100ms
  - Reminder delivery failures > 10/hour
- PagerDuty integration for critical alerts
- Slack integration for warning alerts

**Files to Create**:
- `k8s/monitoring/alert-rules.yaml` - Prometheus alert rules
- `grafana/alerting/contact-points.yaml` - Alert contact points

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Monitoring and Observability (Phase V)
- Section: Observability Requirements → Alerting

**Acceptance Criteria**:
- [ ] High error rate alert triggers
- [ ] High latency alert triggers
- [ ] Kafka consumer lag alert triggers
- [ ] Pod crash looping alert triggers
- [ ] Critical alerts sent to PagerDuty
- [ ] Warning alerts sent to Slack

---

### PH5-MONITOR-003: Configure Distributed Tracing

**Task ID**: PH5-MONITOR-003  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure distributed tracing with Jaeger or Azure Application Insights for end-to-end request tracing.

**Preconditions**:
- Phase IV completed (Jaeger deployed) or Azure Application Insights available

**Expected Output**:
- Distributed tracing configured (Jaeger for dev, Application Insights for prod)
- Dapr configured to export traces
- Trace sampling: 10% production, 100% development
- Traces visible in Jaeger/Azure Portal
- Cross-service trace propagation working

**Files to Create**:
- `k8s/observability/tracing-config.yaml` - Tracing configuration

**Files to Modify**:
- `charts/todo-app/values-aks.yaml` - Configure tracing for cloud

**Related Spec Sections**:
- Section: Observability Requirements → Tracing
- Section: Monitoring and Observability (Phase V)

**Acceptance Criteria**:
- [ ] Traces exported to Jaeger (dev) or Application Insights (prod)
- [ ] Trace includes all service spans
- [ ] Cross-service propagation works
- [ ] Sampling configured correctly
- [ ] Traces queryable via UI

---

## Security & Compliance Tasks

### PH5-SEC-001: Configure Pod Security Standards (Production)

**Task ID**: PH5-SEC-001  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Enforce Pod Security Standards (restricted profile) for production namespace with enhanced security contexts.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Phase IV security tasks completed

**Expected Output**:
- Production namespace labeled: pod-security.kubernetes.io/enforce=restricted
- All deployments use restricted security context
- Non-root user enforced
- Read-only root filesystem enforced
- All capabilities dropped
- seccompProfile configured

**Files to Create**:
- `k8s/security/prod-pod-security.yaml` - Production security standards

**Files to Modify**:
- `charts/todo-app/templates/services/*/deployment.yaml` - Enhanced securityContext

**Related Spec Sections**:
- Section: Security Requirements → Image Security
- Section: Technical Specifications → Kubernetes Manifest Requirements

**Acceptance Criteria**:
- [ ] Production namespace labeled restricted
- [ ] All pods run as non-root
- [ ] Read-only root filesystem enforced
- [ ] All capabilities dropped
- [ ] seccompProfile set to RuntimeDefault

---

### PH5-SEC-002: Configure Network Policies (Production)

**Task ID**: PH5-SEC-002  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure enhanced NetworkPolicies for production with micro-segmentation between services.

**Preconditions**:
- PH5-CLOUD-001 completed (AKS cluster provisioned)
- Azure Network Policy or Calico installed

**Expected Output**:
- Default deny-all NetworkPolicy
- Per-service allow policies with explicit source/destination
- Egress restrictions to external services only
- Dapr sidecar communication allowed
- Kafka and Redis internal only

**Files to Create**:
- `k8s/security/prod-networkpolicies.yaml` - Production NetworkPolicies

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Security Requirements → Network Security
- Section: Technical Specifications → Network Security

**Acceptance Criteria**:
- [ ] Default deny-all policy enforced
- [ ] Per-service policies configured
- [ ] Unauthorized access blocked
- [ ] Authorized access succeeds
- [ ] Egress restricted to allowed destinations

---

### PH5-SEC-003: Configure Audit Logging

**Task ID**: PH5-SEC-003  
**Priority**: P0  
**Estimated Hours**: 3

**Description**: Configure Kubernetes audit logging and application audit trail for compliance requirements.

**Preconditions**:
- PH5-MANAGED-002 completed (Log Analytics configured)
- AKS cluster audit logging enabled

**Expected Output**:
- Kubernetes audit logs sent to Log Analytics
- Application audit events published to Kafka (todo.audit topic)
- Audit trail includes: who accessed what, when, action taken
- Audit logs retained for 90 days
- Audit log search capability

**Files to Create**:
- `k8s/security/audit-logging.yaml` - Audit logging configuration
- `backend/services/audit_service.py` - Application audit service

**Files to Modify**:
- `backend/middleware/audit_middleware.py` - Add audit logging

**Related Spec Sections**:
- Section: Security Requirements → Compliance
- Section: Technical Specifications → Kafka Topic Definitions

**Acceptance Criteria**:
- [ ] Kubernetes audit logs in Log Analytics
- [ ] Application audit events published to Kafka
- [ ] Audit trail includes user, action, timestamp, resource
- [ ] Audit logs retained for 90 days
- [ ] Audit logs searchable via KQL

---

## Migration Tasks

### PH5-MIGRATE-001: Migrate Data from Minikube to Cloud

**Task ID**: PH5-MIGRATE-001  
**Priority**: P0  
**Estimated Hours**: 6

**Description**: Migrate task data from Minikube Redis to Azure Cache for Redis with dual-write strategy for zero downtime.

**Preconditions**:
- PH5-CLOUD-002 completed (Azure Cache provisioned)
- Phase IV application running on Minikube
- PH5-CLOUD-003 completed (Confluent Cloud configured)

**Expected Output**:
- Dual-write implemented (Minikube + Cloud)
- Data synchronization job created
- Cutover procedure documented
- Rollback procedure documented
- Data integrity verified post-migration

**Files to Create**:
- `backend/services/data_migration.py` - Migration service
- `k8s/jobs/data-migration-job.yaml` - Migration job
- `docs/migration/data-migration-runbook.md` - Migration runbook

**Files to Modify**:
- `backend/repositories/task_repository.py` - Add dual-write logic

**Related Spec Sections**:
- Section: Migration Strategy → Data Migration Strategy
- Section: Migration Strategy → Migration Checklist

**Acceptance Criteria**:
- [ ] Dual-write to Minikube and Cloud Redis
- [ ] Data synchronization completes
- [ ] Data integrity verified (checksum match)
- [ ] Cutover succeeds with zero data loss
- [ ] Rollback tested and works

---

### PH5-MIGRATE-002: Migrate Kafka Topics to Confluent Cloud

**Task ID**: PH5-MIGRATE-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Migrate Kafka topics from Bitnami Kafka to Confluent Cloud with message replication and cutover.

**Preconditions**:
- PH5-CLOUD-003 completed (Confluent Cloud configured)
- Phase IV Kafka running on Minikube

**Expected Output**:
- MirrorMaker 2 configured for topic replication
- All topics replicated to Confluent Cloud
- Consumer groups migrated
- Cutover procedure executed
- Old Kafka decommissioned

**Files to Create**:
- `k8s/kafka/mirrormaker2.yaml` - MirrorMaker 2 configuration
- `scripts/kafka-migration.sh` - Migration script

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Migration Strategy → Configuration Changes Matrix
- Section: Technical Specifications → Kafka Topic Definitions

**Acceptance Criteria**:
- [ ] MirrorMaker 2 replicating topics
- [ ] All topics exist in Confluent Cloud
- [ ] Message count matches
- [ ] Consumer groups migrated
- [ ] Cutover succeeds
- [ ] Old Kafka decommissioned

---

### PH5-MIGRATE-003: DNS Cutover to Cloud

**Task ID**: PH5-MIGRATE-003  
**Priority**: P0  
**Estimated Hours**: 2

**Description**: Execute DNS cutover from Minikube to cloud deployment with minimal downtime.

**Preconditions**:
- PH5-CLOUD-005 completed (Cloud ingress with TLS configured)
- PH5-MIGRATE-001 completed (Data migrated)
- PH5-MIGRATE-002 completed (Kafka migrated)
- Cloud deployment verified and stable

**Expected Output**:
- DNS TTL reduced to minimum (5 minutes) 24 hours before cutover
- DNS cutover executed
- Traffic shifted to cloud
- Monitoring during cutover
- Minikube kept as fallback for 48 hours

**Files to Create**:
- `docs/migration/dns-cutover-runbook.md` - DNS cutover runbook

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Migration Strategy → Migration Checklist
- Section: Migration Strategy → Rollback Strategy

**Acceptance Criteria**:
- [ ] DNS TTL reduced 24 hours before
- [ ] DNS cutover executed
- [ ] Traffic visible in cloud (monitoring confirms)
- [ ] Error rate remains < 1% during cutover
- [ ] Minikube kept as fallback for 48 hours
- [ ] Minikube decommissioned after 48 hours stable

---

## Testing Tasks

### PH5-TEST-001: Feature Testing - Recurring Tasks

**Task ID**: PH5-TEST-001  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create comprehensive tests for recurring task functionality including RRULE parsing, next occurrence calculation, and instance creation.

**Preconditions**:
- PH5-FEATURE-001 completed (Recurring tasks implemented)
- Test environment deployed

**Expected Output**:
- Unit tests for RRULE parsing
- Integration tests for recurring instance creation
- E2E tests for complete recurring task flow
- Edge case tests (leap year, timezone changes, etc.)

**Files to Create**:
- `tests/test_recurring_tasks.py` - Recurring task tests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-V-001 (Recurring Tasks)
- Section: Testing Requirements

**Acceptance Criteria**:
- [ ] All RRULE patterns tested (daily, weekly, monthly, yearly)
- [ ] Next occurrence calculation tested
- [ ] Instance creation tested
- [ ] Timezone handling tested
- [ ] Edge cases tested (leap year, month boundaries)
- [ ] Test coverage > 90%

---

### PH5-TEST-002: Feature Testing - Reminders

**Task ID**: PH5-TEST-002  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Create comprehensive tests for reminder functionality including delivery timing, multiple reminders, and notification channels.

**Preconditions**:
- PH5-FEATURE-003 completed (Reminders implemented)
- Test environment deployed

**Expected Output**:
- Unit tests for reminder scheduling
- Integration tests for reminder delivery
- E2E tests for complete reminder flow
- Email delivery tests
- Push notification tests

**Files to Create**:
- `tests/test_reminders.py` - Reminder tests

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-V-003 (Reminders)
- Section: Testing Requirements

**Acceptance Criteria**:
- [ ] Reminder scheduling tested
- [ ] Email delivery tested (mock)
- [ ] Push notification tested (mock)
- [ ] Multiple reminders per task tested
- [ ] Reminder offsets tested (1d, 1h before)
- [ ] Test coverage > 90%

---

### PH5-TEST-003: Performance Testing - Search

**Task ID**: PH5-TEST-003  
**Priority**: P0  
**Estimated Hours**: 4

**Description**: Perform performance testing for search functionality to validate < 100ms P95 latency requirement.

**Preconditions**:
- PH5-SEARCH-003 completed (Search API implemented)
- Elasticsearch cluster deployed
- Load testing tool (k6) installed

**Expected Output**:
- Search performance test script
- Baseline latency measurements
- Load test results (100 concurrent searches)
- Performance optimization recommendations

**Files to Create**:
- `tests/load/search-load-test.js` - Search load test
- `tests/reports/search-performance-report.md` - Performance report

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Requirements → FR-V-006 (Search)
- Section: Non-Functional Requirements → NFR-V-008 (Search Latency)

**Acceptance Criteria**:
- [ ] P95 latency < 100ms with 100 concurrent users
- [ ] P99 latency < 200ms
- [ ] Error rate < 1%
- [ ] Elasticsearch CPU/memory within limits
- [ ] Performance report documents findings

---

### PH5-TEST-004: Migration Testing

**Task ID**: PH5-TEST-004  
**Priority**: P0  
**Estimated Hours**: 6

**Description**: Perform comprehensive migration testing including data integrity, rollback procedure, and cutover validation.

**Preconditions**:
- PH5-MIGRATE-001 completed (Data migration implemented)
- PH5-MIGRATE-002 completed (Kafka migration implemented)
- Staging environment mirrors production

**Expected Output**:
- Migration test plan executed
- Data integrity verified (pre/post migration)
- Rollback procedure tested
- Cutover timing validated
- Migration sign-off document

**Files to Create**:
- `tests/migration/migration-test-plan.md` - Migration test plan
- `tests/reports/migration-test-report.md` - Migration test report

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Migration Strategy
- Section: Testing Requirements → Migration Tests

**Acceptance Criteria**:
- [ ] Data integrity verified (100% match)
- [ ] Rollback procedure tested and works
- [ ] Cutover completes in < 5 minutes
- [ ] Zero data loss during migration
- [ ] Migration sign-off obtained

---

## Documentation Tasks

### PH5-DOC-001: Create Cloud Deployment Documentation

**Task ID**: PH5-DOC-001  
**Priority**: P1  
**Estimated Hours**: 4

**Description**: Create comprehensive cloud deployment documentation including AKS setup, managed services configuration, and operational procedures.

**Preconditions**:
- All PH5-CLOUD-* tasks completed
- All PH5-MANAGED-* tasks completed
- Production deployment stable

**Expected Output**:
- CLOUD-DEPLOYMENT.md: AKS provisioning, managed services setup
- CLOUD-OPERATIONS.md: Day-2 operations, scaling, monitoring
- CLOUD-COST-OPTIMIZATION.md: Cost management strategies

**Files to Create**:
- `docs/phase-v/CLOUD-DEPLOYMENT.md` - Cloud deployment guide
- `docs/phase-v/CLOUD-OPERATIONS.md` - Cloud operations guide
- `docs/phase-v/CLOUD-COST-OPTIMIZATION.md` - Cost optimization guide

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Documentation Standards

**Acceptance Criteria**:
- [ ] CLOUD-DEPLOYMENT.md includes Terraform setup
- [ ] CLOUD-OPERATIONS.md includes scaling procedures
- [ ] CLOUD-COST-OPTIMIZATION.md includes cost analysis
- [ ] All documentation reviewed and approved
- [ ] Documentation tested by following steps

---

### PH5-DOC-002: Create Migration Runbook

**Task ID**: PH5-DOC-002  
**Priority**: P1  
**Estimated Hours**: 4

**Description**: Create detailed migration runbook with step-by-step procedures for migrating from Minikube to AKS/GKE.

**Preconditions**:
- PH5-MIGRATE-003 completed (DNS cutover completed)
- Migration tested in staging

**Expected Output**:
- MIGRATION-RUNBOOK.md: Complete migration procedure
- Pre-migration checklist
- Migration execution steps with timestamps
- Rollback procedure
- Post-migration validation steps

**Files to Create**:
- `docs/phase-v/MIGRATION-RUNBOOK.md` - Complete migration runbook

**Files to Modify**:
- None

**Related Spec Sections**:
- Section: Migration Strategy
- Section: Documentation Standards

**Acceptance Criteria**:
- [ ] Pre-migration checklist complete
- [ ] Step-by-step migration procedure documented
- [ ] Rollback procedure documented
- [ ] Post-migration validation steps documented
- [ ] Runbook tested in staging environment

---

## Task Dependency Graph

```
PH5-FEATURE-001 (Recurring Tasks)
├── PH5-FEATURE-002 (Due Dates)
│   └── PH5-FEATURE-003 (Reminders)
│       └── PH5-DAPRJOB-002 (Reminder Cron)
├── PH5-DAPRJOB-001 (Recurring Cron)
├── PH5-FEATURE-004 (Priority)
├── PH5-FEATURE-005 (Tags)
└── PH5-FEATURE-006 (Search/Filter)
    ├── PH5-SEARCH-001 (Elasticsearch)
    │   └── PH5-SEARCH-002 (Indexing)
    │       └── PH5-SEARCH-003 (Search API)
    └── PH5-EVENT-003 (Search Indexer Processor)

PH5-EVENT-001 (Extend Schemas)
└── PH5-EVENT-002 (Additional Topics)
    └── PH5-EVENT-003 (Event Processors)
        └── PH5-EVENT-004 (DLQ Handling)

PH5-CLOUD-001 (AKS)
├── PH5-CLOUD-002 (Managed Redis)
├── PH5-CLOUD-003 (Confluent Cloud)
├── PH5-CLOUD-004 (Key Vault)
└── PH5-CLOUD-005 (Ingress with TLS)

PH5-MANAGED-001 (Azure Monitor)
├── PH5-MANAGED-002 (Log Analytics)
└── PH5-MANAGED-003 (Managed Grafana)
    └── PH5-MONITOR-001 (Business Dashboards)
    └── PH5-MONITOR-002 (Alert Rules)
    └── PH5-MONITOR-003 (Distributed Tracing)

PH5-CICD-001 (Multi-Env Pipeline)
└── PH5-CICD-002 (Blue-Green)
    └── PH5-CICD-003 (Automated Rollback)

PH5-SEC-001 (Pod Security)
├── PH5-SEC-002 (Network Policies)
└── PH5-SEC-003 (Audit Logging)

PH5-MIGRATE-001 (Data Migration)
├── PH5-MIGRATE-002 (Kafka Migration)
└── PH5-MIGRATE-003 (DNS Cutover)

PH5-TEST-001 (Test Recurring)
PH5-TEST-002 (Test Reminders)
PH5-TEST-003 (Test Search Performance)
PH5-TEST-004 (Test Migration)
└── PH5-DOC-002 (Migration Runbook)

PH5-DOC-001 (Cloud Documentation)
```

---

## Critical Path

**Critical Path**: PH5-CLOUD-001 → PH5-CLOUD-002/003/004/005 → PH5-MANAGED-001/002/003 → PH5-MIGRATE-001 → PH5-MIGRATE-002 → PH5-MIGRATE-003 → PH5-TEST-004 → PH5-DOC-002

**Total Critical Path Duration**: ~38 hours

---

**Version**: 1.0.0  
**Created**: 2026-03-12  
**Status**: Ready for Implementation  
**Prerequisite**: Phase IV completion required  
**Next**: Begin task execution starting with Advanced Features (PH5-FEATURE-001) or Cloud Infrastructure (PH5-CLOUD-001) based on priority
