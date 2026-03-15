# Phase IV: Infrastructure Setup

This directory contains infrastructure setup scripts for Phase IV (Local Kubernetes Deployment).

## Tasks Implemented

| Task ID | Script | Description | Status |
|---------|--------|-------------|--------|
| PH4-INF-001 | `01-setup-minikube.sh` | Setup Minikube Cluster | ✅ Complete |
| PH4-INF-002 | `02-enable-addons.sh` | Enable Minikube Addons | ✅ Complete |
| PH4-INF-003 | `03-install-dapr.sh` | Install Dapr Runtime | ✅ Complete |
| PH4-INF-004 | `04-apply-namespace.sh` | Create Kubernetes Namespace | ✅ Complete |

## Quick Start

Run all infrastructure setup scripts in sequence:

```bash
# Make scripts executable
chmod +x scripts/phase-iv/infrastructure/*.sh

# Run setup scripts in order
./scripts/phase-iv/infrastructure/01-setup-minikube.sh
./scripts/phase-iv/infrastructure/02-enable-addons.sh
./scripts/phase-iv/infrastructure/03-install-dapr.sh
./scripts/phase-iv/infrastructure/04-apply-namespace.sh
```

## Prerequisites

- **Docker**: Running and accessible
- **Minikube**: Installed (`curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`)
- **kubectl**: Installed (`curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl`)
- **Helm 3.x**: Installed (`curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`)
- **System Requirements**: Minimum 8GB RAM, 4 CPU cores, 20GB disk

## Verification

After running all scripts, verify the setup:

```bash
# Verify Minikube cluster
minikube status --profile todo-dev

# Verify addons
minikube addons list --profile todo-dev

# Verify Dapr
kubectl get pods -n dapr-system

# Verify namespace
kubectl get namespace todo-dev
kubectl get resourcequota -n todo-dev
kubectl get limitrange -n todo-dev
```

## Expected Output

After successful setup:

- ✅ Minikube cluster running with 4 CPUs, 4GB RAM, 20GB disk
- ✅ Ingress, metrics-server, and storage-provisioner addons enabled
- ✅ Dapr runtime installed (operator, sentry, placement, dashboard)
- ✅ Namespace `todo-dev` created with ResourceQuota and LimitRange
- ✅ ServiceAccount and RBAC configured

## Next Steps

After infrastructure setup is complete:

1. **PH4-KAFKA**: Install Kafka message broker
2. **PH4-DAPR**: Configure Dapr components (pub/sub, state store, secrets)
3. **PH4-CTR**: Containerize frontend and backend applications
4. **PH4-HELM**: Create Helm charts for deployment

## Troubleshooting

### Minikube fails to start
```bash
# Delete existing cluster and retry
minikube delete --profile todo-dev
./scripts/phase-iv/infrastructure/01-setup-minikube.sh
```

### Dapr installation fails
```bash
# Check cluster is running
minikube status --profile todo-dev

# Retry Dapr installation
dapr uninstall -k
dapr init -k --wait
```

### Namespace creation fails
```bash
# Check cluster context
kubectl config current-context

# Apply namespace manually
kubectl apply -f k8s/namespace.yaml
```

## References

- **Spec**: `specs/features/phase-iv-local-kubernetes.md`
- **Plan**: `specs/features/phase-iv-plan.md`
- **Tasks**: `specs/features/phase-iv-tasks.md`
- **Constitution**: `.specify/memory/phase-iv-v-constitution.md`
