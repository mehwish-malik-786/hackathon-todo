# Phase IV & V Specification Review - Clarification Questions

## Review Summary

**Specifications Reviewed**:
- `specs/features/phase-iv-local-kubernetes.md` (862 lines)
- `specs/features/phase-v-advanced-cloud.md` (1,118 lines)

**Review Date**: 2026-03-12  
**Reviewer**: AI Assistant  
**Status**: ❓ Clarifications Required Before Implementation

---

## Clarification Questions

### 1. Kafka Hosting Choice

**Current Spec Mentions**: Bitnami Kafka (Minikube), Confluent Cloud (Production)

**Questions**:
1.1. For **Minikube/local development**, should we use:
   - **Bitnami Kafka Helm chart** (currently specified)?
   - **Redpanda** (lighter weight, Kafka-compatible)?
   - **Strimzi Kafka Operator** (more production-like locally)?
   
1.2. For **Production (Phase V)**, should we use:
   - **Confluent Cloud** (currently specified, ~$140/month basic)?
   - **Redpanda Cloud** (potentially cheaper, Kafka-compatible)?
   - **Self-managed Kafka on Kubernetes** (more control, more ops overhead)?
   - **Azure Event Hubs** (if AKS, Kafka-compatible)?
   - **Google Pub/Sub with Kafka wrapper** (if GKE)?

1.3. What's the **expected event volume** per day? (affects Kafka partition strategy and cost)

1.4. Do you want **schema registry** for event validation? (Confluent Schema Registry vs Redpanda Schema Registry)

---

### 2. Cloud Provider Selection

**Current Spec Includes**: Both AKS (Azure) and GKE (Google) configurations

**Questions**:
2.1. Which cloud provider should be the **primary target** for Phase V?
   - **Azure AKS** (better enterprise integration, Azure DevOps)?
   - **Google GKE** (Kubernetes-native, better GCP data tools)?
   - **AWS EKS** (not in spec, but most popular)?
   - **Multi-cloud** (support both AKS and GKE simultaneously)?

2.2. What's your **existing cloud relationship**? (credits, existing subscriptions, team expertise)

2.3. For **Phase V budget**, what's the acceptable monthly range?
   - Spec estimates $500-800/month for production
   - Can we optimize to $300-500/month with different choices?

2.4. Do you have **data residency requirements**? (affects region selection)

2.5. Should we prioritize **serverless options**? (Azure Container Apps, Google Cloud Run)

---

### 3. Dapr State Backend

**Current Spec Mentions**: Redis (via Dapr state store)

**Questions**:
3.1. For **Phase IV (Minikube)**:
   - **Redis Helm chart** (currently specified)?
   - **In-memory Dapr state** (simpler, but data lost on restart)?

3.2. For **Phase V (Production)**, should we use:
   - **Redis** (Azure Cache for Redis / Memorystore)?
   - **Neon PostgreSQL** (serverless, currently in Phase III)?
   - **PostgreSQL cluster** (self-managed on Kubernetes)?
   - **Managed PostgreSQL** (Azure Database for PostgreSQL / Cloud SQL)?
   - **Cosmos DB** (if Azure, multi-model)?
   - **Firestore** (if GCP, document store)?

3.3. What's the **data persistence requirement**?
   - Do tasks need to survive service restarts? (yes → need persistent state)
   - Do we need **transactional guarantees**? (PostgreSQL better than Redis)
   - Do we need **complex queries** on task data? (PostgreSQL better)

3.4. Should we use **hybrid approach**?
   - Redis for session/cache (fast)
   - PostgreSQL for persistent task data (durable)

3.5. Current Phase III uses **Neon PostgreSQL** - should we maintain consistency?

---

### 4. Monitoring Stack

**Current Spec Mentions**: Prometheus + Grafana + Jaeger

**Questions**:
4.1. For **Phase IV (Minikube)**:
   - **Prometheus Helm chart** (self-hosted)?
   - **Lightweight alternative** (k3s, minikube addons)?

4.2. For **Phase V (Production)**, should we use:
   - **Self-hosted Prometheus + Grafana** (currently specified, more control)?
   - **Managed Prometheus** (Azure Monitor / Google Cloud Monitoring)?
   - **Grafana Cloud** (managed Grafana, Prometheus, Loki)?
   - **Datadog** (commercial, full-stack observability)?
   - **New Relic** (commercial, good Kubernetes support)?

4.3. What's your **team's monitoring experience**? (affects complexity choice)

4.4. Do you need **business metrics dashboards** (tasks created, active users) or just **technical metrics** (CPU, latency)?

4.5. Should we use **OpenTelemetry** as the standard? (spec mentions it, but needs explicit configuration)

4.6. For **tracing**, should we use:
   - **Jaeger** (currently specified, CNCF project)?
   - **Tempo** (Grafana ecosystem, simpler)?
   - **Managed tracing** (Azure Application Insights / Google Cloud Trace)?

---

### 5. Logging Solution

**Current Spec Mentions**: Fluent Bit + Loki

**Questions**:
5.1. For **Phase IV (Minikube)**:
   - **Fluent Bit + Loki** (currently specified)?
   - **Simpler**: kubectl logs only?
   - **stdout/stderr only** (12-factor app approach)?

5.2. For **Phase V (Production)**, should we use:
   - **Loki + Fluent Bit** (currently specified, lightweight)?
   - **Elasticsearch + Fluentd** (ELK stack, more powerful, heavier)?
   - **Managed logging** (Azure Log Analytics / Google Cloud Logging)?
   - **Datadog Logs** (if using Datadog for metrics)?
   - **Papertrail** (simpler, log aggregation only)?

5.3. What's the **log retention requirement**?
   - Spec says 30 days
   - Is this for compliance/audit or just debugging?

5.4. Do you need **log-based alerting**? (e.g., alert on error patterns)

5.5. Should logs be **searchable by end users** (for their own task history) or just for **ops debugging**?

---

### 6. CI/CD Branching Strategy

**Current Spec Mentions**: GitHub Actions with dev → staging → prod

**Questions**:
6.1. What **branching model** should we use?
   - **GitHub Flow** (main + feature branches, simple)?
   - **Git Flow** (develop, release, main, feature branches)?
   - **Trunk-based development** (short-lived feature branches)?

6.2. For **environment promotion**:
   - **Automatic** (dev on merge, staging on tag, prod on approval)?
   - **Manual** (all environments require approval)?
   - **GitOps** (ArgoCD/Flux watch Git repo for changes)?

6.3. Should we support **multiple feature branches** deployed simultaneously? (preview environments)

6.4. What **approval workflow** for production?
   - **GitHub environment protection** (currently specified)?
   - **Separate approval tool** (PagerDuty, Slack approval)?

6.5. Should CI/CD support **rollback triggers**? (automatic rollback on health check failure)

6.6. Do you need **blue-green** or **canary deployments**? (spec mentions canary in passing)

---

### 7. Multi-Tenant vs Single-User Architecture

**Current Spec**: Appears to assume single-user (user-123 in examples)

**Questions**:
7.1. Is this a **single-user app** (like current Phase I-III)?
   - One user per deployment
   - No authentication needed
   - Simpler architecture

7.2. Or should Phase V support **multi-tenant**?
   - Multiple users per deployment
   - Authentication required (Auth0, Azure AD, Google OAuth)?
   - User isolation (data, events, state)
   - Per-user quotas and limits

7.3. If multi-tenant, what's the **isolation level**?
   - **Logical isolation** (user_id in database, shared infrastructure)?
   - **Physical isolation** (separate namespace per tenant)?
   - **Hybrid** (shared services, isolated data)?

7.4. Should events include **tenant_id** for isolation? (currently only user_id)

7.5. Should we support **team/organization** structure?
   - Shared tasks within team
   - Team-level permissions
   - Admin roles

7.6. If single-user now, should we **design for multi-tenant future**? (add tenant_id to event schemas, even if not used yet)

---

### 8. Additional Clarification Questions

#### 8.1 kubectl-ai and kagent
8.1.1. Are these **mandatory** or **nice-to-have**? (relatively new tools, may have stability issues)
8.1.2. Should we provide **fallback to standard kubectl** commands?

#### 8.2 Frontend Technology
8.2.1. Current spec mentions **React** - is this confirmed?
8.2.2. Should frontend be **containerized separately** or served via backend?

#### 8.3 AI Agent (Phase III Carryover)
8.3.1. Should AI agent use **Qwen2.5** (Phase III) or **OpenAI API** (Phase V)?
8.3.2. Should AI conversations be **event-sourced** via Kafka?

#### 8.4 Database Migration (Phase III → Phase V)
8.4.1. How to **migrate existing tasks** from Phase III Neon PostgreSQL to new architecture?
8.4.2. Should we support **dual-write** during migration?

#### 8.5 Testing Strategy
8.5.1. Should we use **Testcontainers** for integration tests?
8.5.2. What's the **test environment** strategy? (ephemeral per PR, shared staging)

#### 8.6 Security
8.6.1. Should we implement **API authentication** in Phase IV or Phase V?
8.6.2. Do we need **rate limiting** per user/IP?
8.6.3. Should we use **OAuth2/OIDC** or **API keys**?

#### 8.7 Cost Optimization
8.7.1. What's the **priority**: lowest cost or easiest operations?
8.7.2. Should we use **spot instances** for non-critical workloads?
8.7.3. Should we **shut down dev/staging** at night to save costs?

---

## Decision Impact Matrix

| Decision | Affects | Complexity Impact | Cost Impact |
|----------|---------|-------------------|-------------|
| Kafka Choice | Event streaming, ops overhead | High | Medium-High |
| Cloud Provider | All infrastructure | Medium | High |
| State Backend | Data model, queries | Medium | Medium |
| Monitoring | Observability, debugging | Low-Medium | Medium |
| Logging | Debugging, compliance | Low-Medium | Low-Medium |
| CI/CD Strategy | Deployment workflow | Medium | Low |
| Multi-tenant | Architecture, security | Very High | Medium |

---

## Recommended Next Steps

1. **Answer these clarification questions** (prioritize questions 1-7)
2. **Create Architecture Decision Records (ADRs)** for major decisions:
   - ADR-001: Kafka Hosting Choice
   - ADR-002: Cloud Provider Selection
   - ADR-003: State Backend Selection
   - ADR-004: Multi-Tenant vs Single-User
3. **Update specifications** based on decisions
4. **Proceed to architecture plans** (phase-iv-plan.md, phase-v-plan.md)
5. **Create implementation tasks** (phase-iv-tasks.md, phase-v-tasks.md)

---

## Priority Ranking

**Answer These First** (block architecture planning):
1. ✅ Cloud Provider Selection (Q2)
2. ✅ Multi-Tenant vs Single-User (Q7)
3. ✅ Dapr State Backend (Q3)
4. ✅ Kafka Hosting Choice (Q1)

**Answer Second** (before implementation):
5. ✅ Monitoring Stack (Q4)
6. ✅ Logging Solution (Q5)
7. ✅ CI/CD Branching Strategy (Q6)

**Can Decide Later** (during implementation):
8. ✅ Additional questions (Q8.x)

---

**Status**: ⏳ Awaiting User Responses  
**Created**: 2026-03-12  
**Next**: User clarification → ADRs → Updated Specs → Architecture Plans
