#!/bin/bash
# =============================================================================
# Task: PH4-INF-001
# Spec Reference: specs/features/phase-iv-tasks.md → PH4-INF-001
# Description: Setup/Verify Kind Cluster with required resources
# Acceptance Criteria:
#   - Kind cluster running and accessible
#   - Kubernetes version 1.28+
#   - Cluster accessible via kubectl
#   - At least 1 control-plane node ready
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLUSTER_NAME="todo-dev"

echo "=========================================="
echo "Phase IV: Infrastructure Setup"
echo "Task: PH4-INF-001 - Verify Kind Cluster"
echo "=========================================="

# Check prerequisites
echo "[1/5] Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    echo "   Command: sudo systemctl start docker"
    exit 1
fi
echo "✓ Docker is running"

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ Error: Kind is not installed."
    echo "   Install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi
echo "✓ Kind is installed (version: $(kind version))"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed."
    echo "   Install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo "✓ kubectl is installed (version: $(kubectl version --client --short 2>/dev/null | grep -oP 'Client Version: \K.*' || echo 'installed'))"

# Check for existing Kind cluster
echo ""
echo "[2/5] Checking for existing Kind cluster..."
if kind get clusters 2>/dev/null | grep -q "$CLUSTER_NAME"; then
    echo "✓ Kind cluster '$CLUSTER_NAME' already exists"
    USE_EXISTING=true
else
    echo "ℹ️  No existing Kind cluster found"
    USE_EXISTING=false
fi

# Create cluster if not exists
if [ "$USE_EXISTING" = false ]; then
    echo ""
    echo "[3/5] Creating Kind cluster '$CLUSTER_NAME'..."
    
    # Create kind config with port mappings
    cat > /tmp/kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30000-32767
    hostPort: 30000-32767
    protocol: TCP
EOF
    
    kind create cluster --name $CLUSTER_NAME --config /tmp/kind-config.yaml
    rm /tmp/kind-config.yaml
    echo "✓ Kind cluster created successfully"
else
    echo ""
    echo "[3/5] Using existing Kind cluster..."
fi

# Verify cluster status
echo ""
echo "[4/5] Verifying cluster status..."
kubectl cluster-info
echo ""
kubectl get nodes

# Verify system pods
echo ""
echo "[5/5] Verifying system pods..."
kubectl get pods -n kube-system

# Summary
echo ""
echo "=========================================="
echo "✅ PH4-INF-001 Completed Successfully"
echo "=========================================="
echo ""
echo "Cluster Information:"
echo "  - Cluster Name: $CLUSTER_NAME"
echo "  - Kubernetes Version: $(kubectl version --client -o yaml 2>/dev/null | grep gitVersion | head -1 || kubectl version --short 2>/dev/null)"
echo "  - Context: kind-$CLUSTER_NAME"
echo ""
echo "Available Nodes:"
kubectl get nodes -o wide
echo ""
echo "Next Steps:"
echo "  1. Run PH4-INF-002: Install Helm"
echo "  2. Command: ./scripts/phase-iv/infrastructure/02-install-helm.sh"
echo ""
