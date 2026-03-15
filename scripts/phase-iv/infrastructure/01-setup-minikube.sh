#!/bin/bash
# =============================================================================
# Task: PH4-INF-001
# Spec Reference: specs/features/phase-iv-tasks.md → PH4-INF-001
# Description: Setup Minikube Cluster with required resources
# Acceptance Criteria:
#   - Minikube cluster with 4 CPUs, 4GB RAM, 20GB disk
#   - Kubernetes version 1.28+
#   - Cluster accessible via kubectl
# =============================================================================

set -e

# Configuration
MINIKUBE_CPUS=4
MINIKUBE_MEMORY=4096
MINIKUBE_DISK=20gb
MINIKUBE_DRIVER="docker"
KUBERNETES_VERSION="stable"

echo "=========================================="
echo "Phase IV: Infrastructure Setup"
echo "Task: PH4-INF-001 - Setup Minikube Cluster"
echo "=========================================="

# Check prerequisites
echo "[1/6] Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi
echo "✓ Docker is running"

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: Minikube is not installed."
    echo "   Install minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
echo "✓ Minikube is installed (version: $(minikube version --short))"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed."
    echo "   Install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo "✓ kubectl is installed (version: $(kubectl version --client --short 2>/dev/null | grep -oP 'Client Version: \K.*' || kubectl version --client -o yaml | grep gitVersion | head -1))"

# Check available memory
AVAILABLE_MEM=$(free -m | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEM" -lt 6000 ]; then
    echo "⚠️  Warning: Available memory ($AVAILABLE_MEM MB) is less than recommended (6GB)"
else
    echo "✓ Available memory: $AVAILABLE_MEM MB"
fi

# Stop existing minikube cluster if running
echo ""
echo "[2/6] Checking for existing Minikube cluster..."
if minikube status --profile todo-dev 2>/dev/null | grep -q "Running"; then
    echo "⚠️  Existing cluster found. Stopping..."
    minikube stop --profile todo-dev
fi

# Delete existing cluster if it exists
if minikube profile list | grep -q "todo-dev"; then
    echo "⚠️  Existing cluster found. Deleting..."
    minikube delete --profile todo-dev
fi

# Start new Minikube cluster
echo ""
echo "[3/6] Starting Minikube cluster..."
echo "    Configuration:"
echo "      - CPUs: $MINIKUBE_CPUS"
echo "      - Memory: $MINIKUBE_MEMORY MB"
echo "      - Disk: $MINIKUBE_DISK"
echo "      - Driver: $MINIKUBE_DRIVER"
echo "      - Kubernetes Version: $KUBERNETES_VERSION"

minikube start \
    --profile todo-dev \
    --cpus=$MINIKUBE_CPUS \
    --memory=$MINIKUBE_MEMORY \
    --disk-size=$MINIKUBE_DISK \
    --driver=$MINIKUBE_DRIVER \
    --kubernetes-version=$KUBERNETES_VERSION \
    --wait=all

echo "✓ Minikube cluster started successfully"

# Verify cluster status
echo ""
echo "[4/6] Verifying cluster status..."
minikube status --profile todo-dev

# Verify kubectl access
echo ""
echo "[5/6] Verifying kubectl access..."
kubectl cluster-info --context todo-dev

# Verify node resources
echo ""
echo "[6/6] Verifying node resources..."
echo ""
echo "Node Details:"
kubectl describe node minikube | grep -A 5 "Capacity:"
echo ""
echo "Allocatable Resources:"
kubectl describe node minikube | grep -A 5 "Allocatable:"

# Summary
echo ""
echo "=========================================="
echo "✅ PH4-INF-001 Completed Successfully"
echo "=========================================="
echo ""
echo "Cluster Information:"
echo "  - Profile: todo-dev"
echo "  - Kubernetes Version: $(kubectl version --client -o yaml 2>/dev/null | grep gitVersion | head -1 || kubectl version --short 2>/dev/null | grep -oP 'Server Version: \K.*')"
echo "  - Context: todo-dev"
echo ""
echo "Next Steps:"
echo "  1. Run PH4-INF-002: Enable Minikube Addons"
echo "  2. Command: ./scripts/phase-iv/infrastructure/02-enable-addons.sh"
echo ""
