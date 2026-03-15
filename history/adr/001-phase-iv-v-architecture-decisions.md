# ADR-001: Phase IV & V Architecture Decisions

**Date**: 2026-03-14
**Status**: Accepted
**Deciders**: Development Team
**Phase**: Phase IV & V

## Context

We need to make critical architecture decisions for Phase IV (Local Kubernetes) and Phase V (Cloud Production) to proceed with implementation quickly. The spec review identified 8 major clarification questions that must be answered.

## Decision Summary

### 1. Cloud Provider Selection
**Decision**: **Azure AKS** as primary cloud provider
- **Rationale**: Better enterprise integration, existing Azure ecosystem, cost-effective for startups
- **Fallback**: GKE if Azure unavailable

### 2. Kafka Hosting
**Decision**: 
- **Phase IV (Local)**: Bitnami Kafka Helm chart on Minikube
- **Phase V (Production)**: Confluent Cloud (managed Kafka)
- **Rationale**: Minimizes ops overhead, production-ready, schema registry included

### 3. State Backend
**Decision**: **Hybrid Approach**
- **Redis via Dapr**: Session/cache, fast ephemeral state
- **PostgreSQL (Neon)**: Persistent task data (maintain Phase III consistency)
- **Rationale**: Best of both worlds - speed + durability, maintains Phase III investment

### 4. Multi-Tenant vs Single-User
**Decision**: **Single-User with Multi-Tenant Ready Design**
- Start with single-user (user-123 pattern from Phase III)
- Include `tenant_id` and `user_id` in all event schemas
- Design namespaces and data models for future multi-tenancy
- **Rationale**: Faster MVP, migration path ready when needed

### 5. Monitoring Stack
**Decision**:
- **Phase IV**: Prometheus + Grafana + Jaeger (self-hosted via Helm)
- **Phase V**: Grafana Cloud (managed) + Azure Monitor
- **Rationale**: Consistent Grafana ecosystem, managed reduces ops burden

### 6. Logging Solution
**Decision**:
- **Phase IV**: Fluent Bit + Loki (lightweight)
- **Phase V**: Azure Log Analytics + Loki fallback
- **Retention**: 30 days for ops, 90 days for audit
- **Rationale**: Loki is cost-effective, Azure integration for production

### 7. CI/CD Strategy
**Decision**: **GitHub Flow + GitOps**
- **Branching**: GitHub Flow (main + feature branches)
- **Environments**: dev (auto), staging (tag), prod (approval)
- **Deployment**: GitHub Actions → Helm → ArgoCD (Phase V)
- **Rationale**: Simple, industry standard, GitOps ready

### 8. Additional Decisions
- **kubectl-ai/kagent**: Optional, provide standard kubectl fallback
- **Frontend**: React, containerized separately
- **AI Agent**: Maintain Phase III Qwen2.5, events via Kafka
- **Database Migration**: Dual-write during Phase III → Phase V transition
- **Testing**: Testcontainers for integration tests
- **Security**: API keys for Phase IV, OAuth2/OIDC for Phase V
- **Rate Limiting**: Dapr middleware + ingress controller
- **Cost Optimization**: Spot instances for non-critical, shut down dev/staging nights

## Architecture Principles

1. **Dapr First**: All services use Dapr for pub/sub, state, service invocation
2. **Event-Driven**: Kafka for all inter-service communication
3. **Kubernetes Native**: Helm charts, HPA, network policies
4. **Observability**: Metrics, logs, traces from day one
5. **Security by Design**: mTLS, RBAC, secrets management
6. **Cost Conscious**: Optimize for $300-500/month production budget

## Consequences

### Positive
- Fast MVP with single-user focus
- Clear migration path to multi-tenant
- Managed services reduce ops overhead
- Consistent tooling (Grafana ecosystem)
- Cost-effective production deployment

### Negative
- Confluent Cloud costs ~$140/month minimum
- Hybrid state backend adds complexity
- Azure lock-in for Phase V
- Need to maintain Phase III compatibility

### Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Confluent Cloud cost overrun | Medium | Monitor usage, optimize partitions |
| PostgreSQL + Redis complexity | Medium | Clear data ownership rules |
| Azure vendor lock-in | Low | Abstract cloud-specific configs in Helm values |
| Phase III migration issues | Medium | Dual-write strategy, extensive testing |

## Compliance

This ADR complies with:
- `.specify/memory/constitution.md` - Core project principles
- `.specify/memory/phase-iv-v-constitution.md` - Cloud-native constitution
- Phase III architecture - Maintains compatibility

## References

- Spec: `specs/features/phase-iv-local-kubernetes.md`
- Spec: `specs/features/phase-v-advanced-cloud.md`
- Constitution: `.specify/memory/phase-iv-v-constitution.md`
- PHR: `history/prompts/features/phase-iv-v/`
