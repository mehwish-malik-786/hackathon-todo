#!/bin/bash
# =============================================================================
# Demo Video Setup Script - Phase IV
# Quick setup for demo video recording
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
echo "  🎬 Phase IV Demo Video Setup"
echo "  Quick deployment for demo recording"
echo "========================================================================="
echo ""

# Add kubectl to PATH
export PATH="$PROJECT_ROOT:$PATH"

# Step 1: Check Minikube
log_step "1" "Checking Minikube status..."
if ! minikube status &>/dev/null; then
    log_info "Starting Minikube..."
    minikube start --cpus=4 --memory=4096 --driver=docker
else
    log_success "Minikube is running"
fi

# Step 2: Create Namespace
log_step "2" "Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
log_success "Namespace created"

# Step 3: Install Kafka (if not exists)
log_step "3" "Setting up Kafka..."
if ! helm status kafka -n $NAMESPACE &>/dev/null; then
    log_info "Installing Kafka..."
    helm install kafka bitnami/kafka -n $NAMESPACE \
        --set replicaCount=1 \
        --set persistence.enabled=false \
        --set volumePermissions.enabled=true \
        --wait --timeout 5m
    log_success "Kafka installed"
else
    log_success "Kafka already exists"
fi

# Step 4: Install Redis (if not exists)
log_step "4" "Setting up Redis..."
if ! helm status redis -n $NAMESPACE &>/dev/null; then
    log_info "Installing Redis..."
    helm install redis bitnami/redis -n $NAMESPACE \
        --set architecture=standalone \
        --set auth.enabled=false \
        --set persistence.enabled=false \
        --wait --timeout 3m
    log_success "Redis installed"
else
    log_success "Redis already exists"
fi

# Step 5: Deploy Dapr
log_step "5" "Setting up Dapr..."
if ! dapr status -k -n $NAMESPACE &>/dev/null | grep -q "running"; then
    log_info "Installing Dapr..."
    dapr init -k -n $NAMESPACE --wait
    log_success "Dapr installed"
else
    log_success "Dapr already exists"
fi

# Step 6: Deploy Dapr Components
log_step "6" "Configuring Dapr components..."
kubectl apply -f $PROJECT_ROOT/k8s/dapr-components.yaml -n $NAMESPACE
log_success "Dapr components configured"

# Step 7: Deploy Application
log_step "7" "Deploying Todo application..."
kubectl apply -f $PROJECT_ROOT/k8s/namespace.yaml
kubectl apply -f $PROJECT_ROOT/k8s/backend-deployment.yaml -n $NAMESPACE
kubectl apply -f $PROJECT_ROOT/k8s/frontend-deployment.yaml -n $NAMESPACE
log_success "Application deployed"

# Step 8: Wait for pods
log_step "8" "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=120s || true

# Step 9: Show status
echo ""
echo "========================================================================="
log_success "Demo Setup Complete!"
echo "========================================================================="
echo ""
log_info "Getting service URLs..."
echo ""

# Get URLs
BACKEND_URL=$(kubectl get service backend -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
FRONTEND_URL=$(minikube service frontend -n $NAMESPACE --url 2>/dev/null | head -1)

echo "📊 Application Status:"
echo "-------------------------------------------------------------------------"
kubectl get pods -n $NAMESPACE -o wide
echo ""
echo "🔗 Service Endpoints:"
echo "-------------------------------------------------------------------------"
echo "  Backend:  http://$BACKEND_URL:7860"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo "🎬 Demo Commands for Video:"
echo "-------------------------------------------------------------------------"
echo "  # Check pods status:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "  # Check services:"
echo "  kubectl get svc -n $NAMESPACE"
echo ""
echo "  # View backend logs:"
echo "  kubectl logs -n $NAMESPACE -l app=backend -f"
echo ""
echo "  # Test backend API:"
echo "  curl http://$BACKEND_URL:7860/health"
echo ""
echo "  # Access frontend:"
echo "  minikube service frontend -n $NAMESPACE --url"
echo ""
echo "========================================================================="
echo "  Ready for demo video recording! 🎥"
echo "========================================================================="
