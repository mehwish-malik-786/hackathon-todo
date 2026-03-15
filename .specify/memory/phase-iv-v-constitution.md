# Phase IV & V: Cloud-Native Todo Chatbot Constitution

## Core Principles

### I. Containerization First
All services must be containerized using Docker. Every microservice runs in an isolated container with minimal base images. Multi-stage builds mandatory for production images. No direct host dependencies allowed.

### II. Kubernetes-Native Deployment
- **Local Development**: Minikube required for local Kubernetes cluster
- **Production Ready**: Must support migration to AKS (Azure Kubernetes Service) or GKE (Google Kubernetes Engine) without code changes
- **Configuration**: Environment-specific configs via ConfigMaps and Secrets only
- **No Manual kubectl**: Use kubectl-ai and kagent for intelligent cluster operations

### III. Helm Chart Standardization
All deployments must use Helm charts for package management. Charts must be:
- Versioned following semantic versioning
- Support multiple environments (dev, staging, prod)
- Include rollback capabilities
- Document all values and overrides

### IV. Dapr Microservices Building Blocks
Mandatory Dapr integration for all services:
- **Pub/Sub**: Event-driven communication via Dapr pub/sub
- **State Management**: Use Dapr state store for persistence
- **Service Invocation**: Dapr sidecar for inter-service calls
- **Secrets**: Dapr secrets integration or Kubernetes Secrets
- **No Direct Coupling**: Services communicate only through Dapr APIs

### V. Event-Driven Architecture (NON-NEGOTIABLE)
- **Kafka-Compatible**: All events must flow through Kafka-compatible message broker
- **Async First**: Synchronous calls prohibited except for health checks
- **Event Sourcing**: State changes captured as immutable events
- **CQRS Pattern**: Command and Query Responsibility Segregation mandatory
- **No Direct Database Access**: Services access data only through event streams or Dapr state

### VI. Independent Scalability
Each microservice must scale independently:
- Horizontal Pod Autoscaler (HPA) configured per service
- Resource limits and requests defined per container
- No shared state between service instances
- Stateless design with externalized state via Dapr

### VII. Security by Design
- **Secrets Management**: Kubernetes Secrets or Dapr Secrets only - no environment variables for sensitive data
- **Network Policies**: Zero-trust networking between pods
- **RBAC**: Role-Based Access Control for all service accounts
- **mTLS**: Mutual TLS for service-to-service communication via Dapr
- **Image Scanning**: All Docker images scanned for vulnerabilities in CI/CD

### VIII. Observability Requirements
- **Distributed Tracing**: OpenTelemetry integration via Dapr
- **Metrics**: Prometheus-compatible metrics exposed by all services
- **Logging**: Structured JSON logs with correlation IDs
- **Health Checks**: Liveness, readiness, and startup probes mandatory
- **Dashboards**: Grafana dashboards for all critical metrics

### IX. CI/CD Automation
- **GitHub Actions**: All CI/CD pipelines must use GitHub Actions
- **Automated Testing**: Unit, integration, and end-to-end tests in pipeline
- **Image Build**: Automated Docker build and push on merge
- **Helm Lint**: Chart validation in CI
- **GitOps Ready**: Support for ArgoCD or Flux (optional)

### X. Spec-Driven Development (NON-NEGOTIABLE)
- **No Manual Coding**: All code changes follow Spec-Driven workflow
- **PHR Required**: Prompt History Records for all development
- **ADR for Decisions**: Architectural Decision Records for significant choices
- **Test-First**: Tests written before implementation
- **Documentation**: All features documented in specs/ directory

## Architecture Principles

### Microservices Boundaries
- **Frontend Service**: React UI with chat interface
- **Backend API Service**: REST/GraphQL API gateway
- **AI Agent Service**: LLM integration and intent classification
- **Task Service**: Task CRUD operations (CQRS command side)
- **Query Service**: Task queries and projections (CQRS query side)
- **Event Processor Service**: Kafka event stream processing

### Communication Patterns
- **Sync**: API Gateway → Services (HTTP/gRPC via Dapr)
- **Async**: Service → Service (Events via Dapr Pub/Sub + Kafka)
- **State**: Services → Dapr State Store (Redis/CosmosDB/PostgreSQL)

### Data Flow
```
User → Frontend → API Gateway → [Dapr Invoke] → Service
Service → [Dapr Pub/Sub] → Kafka → Event Processor → State Store
Service → [Dapr State] → State Store (no direct DB access)
```

## Security Constraints

### Secrets Management
- **Development**: Kubernetes Secrets with base64 encoding
- **Production**: Dapr Secrets with Azure Key Vault / GCP Secret Manager / AWS Secrets Manager
- **Rotation**: Automated secret rotation policy (90 days max)
- **Access**: RBAC policies restrict secret access per service

### Network Security
- **NetworkPolicies**: Deny-all default, explicit allow rules only
- **Ingress**: Single ingress controller with TLS termination
- **Service Mesh**: Dapr provides mTLS out of the box
- **Pod Security**: PodSecurityPolicies/Standards enforced

### Image Security
- **Base Images**: Alpine or distroless images only
- **Scanning**: Trivy/Snyk in CI pipeline
- **Signing**: Cosign image signing (production)
- **Updates**: Automated security patch updates

## Scalability Rules

### Horizontal Scaling
- **HPA Configuration**: CPU/Memory-based autoscaling (min 2, max 10 replicas)
- **Custom Metrics**: Kafka lag, request queue depth for advanced scaling
- **Pod Disruption Budget**: Minimum 50% availability during updates

### Resource Management
- **Requests**: Minimum viable resources for baseline operation
- **Limits**: Hard caps to prevent resource starvation
- **QoS Classes**: Guaranteed or Burstable only (no BestEffort)

### State Scaling
- **Dapr State Store**: Redis Cluster or managed CosmosDB
- **Kafka**: Partitioned topics for parallel processing
- **Sharding**: Event partitioning by session_id or tenant_id

## Observability Requirements

### Logging Standards
- **Format**: Structured JSON only
- **Fields**: timestamp, level, service, trace_id, span_id, message
- **Aggregation**: Fluentd/Fluent Bit → Elasticsearch or Loki
- **Retention**: 30 days minimum

### Metrics Standards
- **Endpoint**: `/metrics` (Prometheus format)
- **Naming**: `<service>_<metric_name>_total`
- **Labels**: service, pod, namespace, environment
- **Dashboards**: Grafana per service + system overview

### Tracing Standards
- **Propagation**: W3C Trace Context via Dapr
- **Sampling**: 10% production, 100% development
- **Export**: Jaeger or Zipkin compatible
- **Correlation**: Trace ID in all logs

## Deployment Standards

### Helm Chart Structure
```
charts/
├── todo-app/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-prod.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── ingress.yaml
│   │   ├── networkpolicy.yaml
│   │   └── dapr-components/
│   │       ├── pubsub.yaml
│   │       ├── statestore.yaml
│   │       └── secretstore.yaml
```

### Kubernetes Manifest Requirements
- **Labels**: app, version, team, environment
- **Annotations**: prometheus scrape, dapr enabled
- **Probes**: liveness, readiness, startup (all three)
- **SecurityContext**: non-root, read-only rootfs, drop capabilities

### Environment Promotion
- **Dev**: Auto-deploy on merge to main
- **Staging**: Manual approval, integration tests
- **Prod**: Manual approval, canary deployment

## Migration Strategy: Minikube → AKS/GKE

### Infrastructure Abstraction
- **No Cloud-Specific Code**: All cloud provider logic in Helm values only
- **Dapr Components**: Provider-specific configs in component YAML (not code)
- **Secrets**: Dapr secret store abstraction handles provider differences

### Migration Checklist
1. Export Helm values from Minikube
2. Create cloud-specific values file (aks-values.yaml / gke-values.yaml)
3. Update Dapr component configs for managed services
4. Configure cloud provider ingress controller
5. Migrate secrets to cloud Key Vault (optional)
6. Update DNS and TLS certificates
7. Cutover traffic via ingress

### Testing Migration
- **Smoke Tests**: Run against both environments
- **Load Tests**: Validate scaling behavior
- **Chaos Tests**: Network partitions, pod failures

## Governance

### Compliance Verification
- All PRs must verify constitution compliance
- CI pipeline includes constitution checks
- Complexity must be justified with ADR
- Use `.specify/memory/` for runtime development guidance

### Amendment Process
- Constitution changes require ADR
- Migration plan required for breaking changes
- All team members must acknowledge changes

### Quality Gates
- **Constitution Check**: Automated validation in CI
- **Helm Lint**: Chart validation mandatory
- **Security Scan**: No critical vulnerabilities
- **Test Coverage**: Minimum 80% unit test coverage
- **Integration Tests**: All service contracts tested

---

**Version**: 1.0.0 | **Ratified**: 2026-03-12 | **Last Amended**: 2026-03-12

**Status**: DRAFT - Awaiting User Approval
