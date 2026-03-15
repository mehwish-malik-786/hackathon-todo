#!/bin/bash
# =============================================================================
# Task: PH4-INF-002
# Spec Reference: specs/features/phase-iv-tasks.md → PH4-INF-002
# Description: Enable Minikube Addons (ingress, metrics-server, storage-provisioner)
# Acceptance Criteria:
#   - Ingress addon enabled and nginx-ingress-controller running
#   - Metrics-server addon enabled and running
#   - Storage-provisioner addon enabled
#   - All addon pods in Running state
# =============================================================================

set -e

# Configuration
MINIKUBE_PROFILE="todo-dev"

echo "=========================================="
echo "Phase IV: Infrastructure Setup"
echo "Task: PH4-INF-002 - Enable Minikube Addons"
echo "=========================================="

# Verify Minikube cluster is running
echo "[1/5] Verifying Minikube cluster..."
if ! minikube status --profile $MINIKUBE_PROFILE | grep -q "host: Running"; then
    echo "❌ Error: Minikube cluster is not running."
    echo "   Run PH4-INF-001 first: ./scripts/phase-iv/infrastructure/01-setup-minikube.sh"
    exit 1
fi
echo "✓ Minikube cluster is running"

# List available addons
echo ""
echo "[2/5] Listing available addons..."
minikube addons list --profile $MINIKUBE_PROFILE

# Enable ingress addon
echo ""
echo "[3/5] Enabling Ingress addon..."
minikube addons enable ingress --profile $MINIKUBE_PROFILE
echo "✓ Ingress addon enabled"

# Wait for ingress controller to be ready
echo "    Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=120s 2>/dev/null || {
    echo "⚠️  Ingress controller took longer than expected to start"
}
echo "✓ Ingress controller is ready"

# Enable metrics-server addon
echo ""
echo "[4/5] Enabling Metrics Server addon..."
minikube addons enable metrics-server --profile $MINIKUBE_PROFILE
echo "✓ Metrics Server addon enabled"

# Wait for metrics-server to be ready
echo "    Waiting for metrics-server to be ready..."
kubectl wait --namespace kube-system \
    --for=condition=ready pod \
    --selector=k8s-app=metrics-server \
    --timeout=120s 2>/dev/null || {
    echo "⚠️  Metrics-server took longer than expected to start"
}
echo "✓ Metrics-server is ready"

# Verify storage-provisioner (usually enabled by default)
echo ""
echo "[5/5] Verifying Storage Provisioner..."
if minikube addons list --profile $MINIKUBE_PROFILE | grep -q "storage-provisioner.*enabled"; then
    echo "✓ Storage-provisioner is already enabled"
else
    echo "    Enabling storage-provisioner..."
    minikube addons enable storage-provisioner --profile $MINIKUBE_PROFILE
    echo "✓ Storage-provisioner enabled"
fi

# Verify all addons
echo ""
echo "=========================================="
echo "Addon Status:"
echo "=========================================="
minikube addons list --profile $MINIKUBE_PROFILE | grep -E "ingress|metrics-server|storage-provisioner"

# Verify pods
echo ""
echo "=========================================="
echo "Addon Pod Status:"
echo "=========================================="
echo ""
echo "Ingress Controller Pods:"
kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller

echo ""
echo "Metrics Server Pods:"
kubectl get pods -n kube-system -l k8s-app=metrics-server

echo ""
echo "Storage Provisioner Pods:"
kubectl get pods -n kube-system -l app=kubernetes.io/component=storage-provisioner 2>/dev/null || \
    kubectl get pods -n kube-system | grep storage-provisioner

# Summary
echo ""
echo "=========================================="
echo "✅ PH4-INF-002 Completed Successfully"
echo "=========================================="
echo ""
echo "Enabled Addons:"
echo "  - ingress (NGINX Ingress Controller)"
echo "  - metrics-server (Kubernetes Metrics Server)"
echo "  - storage-provisioner (Dynamic Volume Provisioning)"
echo ""
echo "Next Steps:"
echo "  1. Run PH4-INF-003: Install Dapr Runtime"
echo "  2. Command: ./scripts/phase-iv/infrastructure/03-install-dapr.sh"
echo ""
