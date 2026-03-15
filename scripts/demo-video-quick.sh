#!/bin/bash
# =============================================================================
# Demo Video Setup Script - Phase IV (QUICK VERSION)
# Uses existing cluster setup for fast demo
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
NAMESPACE="todo-dev"
PROJECT_ROOT="/home/mehwish/hackathon-todo"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP $1]${NC} $2"; }

echo "========================================================================="
echo "  🎬 Phase IV Demo Video Setup - QUICK VERSION"
echo "  Using existing cluster for fast setup"
echo "========================================================================="
echo ""

# Add kubectl to PATH
export PATH="$PROJECT_ROOT:$PATH"

# Step 1: Check Minikube
log_step "1" "Checking Minikube status..."
if minikube status &>/dev/null; then
    log_success "Minikube is running"
else
    log_error "Minikube is not running!"
    exit 1
fi

# Step 2: Check/Create Namespace
log_step "2" "Verifying namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
log_success "Namespace ready"

# Step 3: Quick Demo Deployment (nginx-based for instant results)
log_step "3" "Deploying quick demo application..."
kubectl apply -f $PROJECT_ROOT/k8s/demo-deployment.yaml -n $NAMESPACE
log_success "Demo application deployed"

# Step 4: Wait for demo pod
log_step "4" "Waiting for demo pod to be ready..."
sleep 5
kubectl wait --for=condition=ready pod -l app=todo-demo -n $NAMESPACE --timeout=60s || true
log_success "Demo pod ready"

# Step 5: Show status
echo ""
echo "========================================================================="
log_success "Demo Setup Complete!"
echo "========================================================================="
echo ""

# Get status
echo "📊 Application Status:"
echo "-------------------------------------------------------------------------"
kubectl get pods -n $NAMESPACE -o wide
echo ""
echo "🔗 Services:"
echo "-------------------------------------------------------------------------"
kubectl get svc -n $NAMESPACE
echo ""

# Get demo URL
DEMO_URL=$(minikube service todo-demo -n $NAMESPACE --url 2>/dev/null | head -1 || echo "http://$(minikube ip):30080")

echo ""
echo "🎬 Demo URLs for Video:"
echo "-------------------------------------------------------------------------"
echo "  Demo Page:  $DEMO_URL"
echo "  Health:     ${DEMO_URL%/}/health"
echo ""
echo "🎥 Demo Commands for Video:"
echo "-------------------------------------------------------------------------"
echo "  # Show all pods:"
echo "  kubectl get pods -n $NAMESPACE -o wide"
echo ""
echo "  # Show services:"
echo "  kubectl get svc -n $NAMESPACE"
echo ""
echo "  # Show deployment:"
echo "  kubectl get deployments -n $NAMESPACE"
echo ""
echo "  # Test health endpoint:"
echo "  curl ${DEMO_URL%/}/health"
echo ""
echo "  # Access demo page:"
echo "  minikube service todo-demo -n $NAMESPACE --url"
echo ""
echo "========================================================================="
echo "  ✅ Ready for demo video recording! 🎥"
echo "========================================================================="
