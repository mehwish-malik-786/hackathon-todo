#!/bin/bash
# =============================================================================
# Task: PH4-INF-004
# Spec Reference: specs/features/phase-iv-tasks.md → PH4-INF-004
# Description: Apply and verify Kubernetes Namespace configuration
# =============================================================================

set -e

MINIKUBE_PROFILE="todo-dev"

echo "=========================================="
echo "Phase IV: Infrastructure Setup"
echo "Task: PH4-INF-004 - Create Kubernetes Namespace"
echo "=========================================="

# Verify Minikube cluster is running
echo "[1/4] Verifying Minikube cluster..."
if ! minikube status --profile $MINIKUBE_PROFILE | grep -q "host: Running"; then
    echo "❌ Error: Minikube cluster is not running."
    exit 1
fi
echo "✓ Minikube cluster is running"

# Verify Dapr is installed
echo ""
echo "[2/4] Verifying Dapr installation..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo "❌ Error: Dapr is not installed."
    echo "   Run PH4-INF-003 first: ./scripts/phase-iv/infrastructure/03-install-dapr.sh"
    exit 1
fi
echo "✓ Dapr is installed"

# Apply namespace configuration
echo ""
echo "[3/4] Applying namespace configuration..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname $(dirname $(dirname "$SCRIPT_DIR")))"

kubectl apply -f "$PROJECT_ROOT/k8s/namespace.yaml"
echo "✓ Namespace configuration applied"

# Verify namespace
echo ""
echo "[4/4] Verifying namespace setup..."
echo ""
echo "Namespace Details:"
kubectl get namespace todo-dev

echo ""
echo "ResourceQuota:"
kubectl get resourcequota -n todo-dev

echo ""
echo "LimitRange:"
kubectl get limitrange -n todo-dev

echo ""
echo "ServiceAccount:"
kubectl get serviceaccount todo-app-sa -n todo-dev

echo ""
echo "Role:"
kubectl get role todo-app-role -n todo-dev

echo ""
echo "RoleBinding:"
kubectl get rolebinding todo-app-rolebinding -n todo-dev

echo ""
echo "Namespace Labels:"
kubectl get namespace todo-dev --show-labels

# Summary
echo ""
echo "=========================================="
echo "✅ PH4-INF-004 Completed Successfully"
echo "=========================================="
echo ""
echo "Namespace Configuration:"
echo "  - Namespace: todo-dev"
echo "  - ResourceQuota: 8 CPU cores, 8Gi memory"
echo "  - LimitRange: Default container limits configured"
echo "  - ServiceAccount: todo-app-sa"
echo "  - RBAC: Role and RoleBinding configured"
echo ""
echo "Infrastructure Tasks Complete!"
echo ""
echo "Next Steps:"
echo "  1. Proceed to PH4-CTR tasks (Containerization)"
echo "  2. Or proceed to PH4-KAFKA tasks (Kafka setup)"
echo "  3. Or proceed to PH4-DAPR tasks (Dapr components)"
echo ""
echo "Recommended Next Task:"
echo "  PH4-KAFKA-001: Install Kafka on Minikube"
echo "  Command: ./scripts/phase-iv/kafka/01-install-kafka.sh"
echo ""
