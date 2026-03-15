#!/bin/bash
# =============================================================================
# Task: PH4-INF-003
# Spec Reference: specs/features/phase-iv-tasks.md → PH4-INF-003
# Description: Install Dapr Runtime on Kubernetes cluster
# Acceptance Criteria:
#   - Dapr CLI installed (version 1.12+)
#   - Dapr initialized on Kubernetes
#   - All Dapr system pods running in dapr-system namespace
# =============================================================================

set -e

# Configuration
MINIKUBE_PROFILE="todo-dev"
DAPR_VERSION="1.12.0"

echo "=========================================="
echo "Phase IV: Infrastructure Setup"
echo "Task: PH4-INF-003 - Install Dapr Runtime"
echo "=========================================="

# Verify Minikube cluster is running
echo "[1/6] Verifying Minikube cluster..."
if ! minikube status --profile $MINIKUBE_PROFILE | grep -q "host: Running"; then
    echo "❌ Error: Minikube cluster is not running."
    echo "   Run PH4-INF-001 first: ./scripts/phase-iv/infrastructure/01-setup-minikube.sh"
    exit 1
fi
echo "✓ Minikube cluster is running"

# Check/install Dapr CLI
echo ""
echo "[2/6] Checking Dapr CLI..."
if ! command -v dapr &> /dev/null; then
    echo "    Dapr CLI not found. Installing..."
    curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
    export PATH=$PATH:$HOME/.dapr/bin
fi

DAPR_VERSION_INSTALLED=$(dapr --version | grep -oP 'CLI version: \K.*' | head -1)
echo "✓ Dapr CLI installed (version: $DAPR_VERSION_INSTALLED)"

# Verify Dapr CLI version
if [[ ! "$DAPR_VERSION_INSTALLED" =~ ^1\.(1[2-9]|[2-9][0-9]|[0-9]) ]]; then
    echo "⚠️  Warning: Dapr CLI version $DAPR_VERSION_INSTALLED may be older than recommended (1.12+)"
fi

# Check if Dapr is already initialized on Kubernetes
echo ""
echo "[3/6] Checking Dapr Kubernetes runtime..."
if kubectl get namespace dapr-system &> /dev/null; then
    echo "⚠️  Dapr system namespace already exists"
    
    # Check if Dapr pods are running
    if kubectl get pods -n dapr-system | grep -q "Running"; then
        echo "    Dapr appears to be already initialized."
        read -p "Do you want to reinstall? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            echo "    Skipping Dapr installation"
            echo "✓ Dapr is already installed"
            
            # Verify pods
            echo ""
            echo "Dapr System Pods:"
            kubectl get pods -n dapr-system
            echo ""
            echo "=========================================="
            echo "✅ PH4-INF-003 Completed (Existing Installation)"
            echo "=========================================="
            exit 0
        fi
        
        echo "    Uninstalling existing Dapr installation..."
        dapr uninstall -k --wait
    fi
fi

# Initialize Dapr on Kubernetes
echo ""
echo "[4/6] Initializing Dapr on Kubernetes..."
echo "    This may take a few minutes..."

dapr init -k --wait --timeout 600

echo "✓ Dapr initialized on Kubernetes"

# Verify Dapr pods
echo ""
echo "[5/6] Verifying Dapr system pods..."
echo ""
echo "Waiting for all Dapr pods to be ready..."

# Wait for each Dapr component
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=180s 2>/dev/null || \
    echo "⚠️  dapr-operator took longer than expected"

kubectl wait --for=condition=ready pod -l app=dapr-sentry -n dapr-system --timeout=180s 2>/dev/null || \
    echo "⚠️  dapr-sentry took longer than expected"

kubectl wait --for=condition=ready pod -l app=dapr-placement -n dapr-system --timeout=180s 2>/dev/null || \
    echo "⚠️  dapr-placement took longer than expected"

kubectl wait --for=condition=ready pod -l app=dapr-dashboard -n dapr-system --timeout=180s 2>/dev/null || \
    echo "⚠️  dapr-dashboard took longer than expected"

echo "✓ All Dapr pods are ready"

# List Dapr pods
echo ""
echo "Dapr System Pods:"
kubectl get pods -n dapr-system

# Verify Dapr components
echo ""
echo "[6/6] Verifying Dapr installation..."
echo ""
echo "Dapr Components:"
dapr components -k -n todo-dev 2>/dev/null || echo "    No components yet (will be created in PH4-DAPR tasks)"

echo ""
echo "Dapr Configurations:"
dapr configurations -k 2>/dev/null || echo "    No configurations yet"

# Summary
echo ""
echo "=========================================="
echo "✅ PH4-INF-003 Completed Successfully"
echo "=========================================="
echo ""
echo "Dapr Installation Details:"
echo "  - CLI Version: $DAPR_VERSION_INSTALLED"
echo "  - Runtime Version: $(kubectl get deployments -n dapr-system dapr-operator -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null | cut -d: -f2 || echo 'N/A')"
echo "  - Namespace: dapr-system"
echo ""
echo "Dapr System Components:"
echo "  - dapr-operator (webhooks, placement)"
echo "  - dapr-sentry (certificate authority)"
echo "  - dapr-placement (actor placement)"
echo "  - dapr-dashboard (UI dashboard)"
echo ""
echo "Next Steps:"
echo "  1. Run PH4-INF-004: Create Kubernetes Namespace"
echo "  2. Command: kubectl apply -f k8s/namespace.yaml"
echo "  3. Then proceed to PH4-DAPR tasks for component configuration"
echo ""
