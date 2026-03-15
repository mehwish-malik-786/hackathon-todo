#!/bin/bash
# =============================================================================
# Phase IV: Complete Deployment Script
# Description: Automated deployment of Todo App to Minikube with Dapr, Kafka, Redis
# Usage: ./scripts/deploy-phase-iv.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="todo-dev"
MINIKUBE_PROFILE="todo-phase-iv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing=()
    
    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v kubectl >/dev/null 2>&1 || missing+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing+=("helm")
    command -v minikube >/dev/null 2>&1 || missing+=("minikube")
    command -v dapr >/dev/null 2>&1 || missing+=("dapr")
    
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        echo "Please install missing tools and try again."
        exit 1
    fi
    
    log_success "All prerequisites installed"
}

setup_minikube() {
    log_info "Setting up Minikube cluster..."
    
    if minikube status -p "$MINIKUBE_PROFILE" &> /dev/null; then
        log_warning "Minikube cluster already exists"
        read -p "Do you want to delete and recreate it? (y/n): " confirm
        if [[ $confirm == [yY] ]]; then
            minikube delete -p "$MINIKUBE_PROFILE"
        else
            log_info "Using existing cluster"
            minikube profile "$MINIKUBE_PROFILE"
            return
        fi
    fi
    
    minikube start \
        --profile "$MINIKUBE_PROFILE" \
        --cpus=4 \
        --memory=4096 \
        --disk-size=20gb \
        --driver=docker \
        --kubernetes-version=1.28.0 \
        --cni=calico
    
    log_success "Minikube cluster started"
}

enable_addons() {
    log_info "Enabling Minikube addons..."
    
    minikube addons enable ingress -p "$MINIKUBE_PROFILE"
    minikube addons enable metrics-server -p "$MINIKUBE_PROFILE"
    minikube addons enable storage-provisioner -p "$MINIKUBE_PROFILE"
    
    # Wait for addons to be ready
    log_info "Waiting for addons to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx --timeout=120s
    kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=120s
    
    log_success "Addons enabled"
}

install_dapr() {
    log_info "Installing Dapr runtime..."
    
    if kubectl get namespace dapr-system &> /dev/null; then
        log_warning "Dapr already installed"
        dapr init -k --wait
    else
        dapr init -k --wait
    fi
    
    log_success "Dapr runtime installed"
}

create_namespace() {
    log_info "Creating namespace $NAMESPACE..."
    
    kubectl apply -f "$PROJECT_ROOT/k8s/namespace.yaml"
    
    # Wait for namespace to be ready
    kubectl wait --for=condition=ready namespace "$NAMESPACE" --timeout=60s
    
    log_success "Namespace created"
}

install_kafka() {
    log_info "Installing Kafka..."
    
    # Add Bitnami Helm repository
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    # Install Kafka
    helm upgrade --install kafka bitnami/kafka \
        --namespace "$NAMESPACE" \
        --set replicaCount=1 \
        --set persistence.size=5Gi \
        --set resources.requests.cpu=100m \
        --set resources.requests.memory=256Mi \
        --set resources.limits.cpu=500m \
        --set resources.limits.memory=512Mi \
        --wait --timeout 5m
    
    # Wait for Kafka to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n "$NAMESPACE" --timeout=300s
    
    log_success "Kafka installed"
}

install_redis() {
    log_info "Installing Redis..."
    
    # Install Redis
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set architecture=standalone \
        --set auth.enabled=false \
        --set master.resources.requests.cpu=100m \
        --set master.resources.requests.memory=128Mi \
        --wait --timeout 3m
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=120s
    
    log_success "Redis installed"
}

install_dapr_components() {
    log_info "Installing Dapr components..."
    
    kubectl apply -f "$PROJECT_ROOT/k8s/dapr-components.yaml"
    
    # Wait for components to be ready
    sleep 5
    
    log_success "Dapr components installed"
}

build_and_deploy_app() {
    log_info "Building and deploying application..."
    
    # Build backend image
    if [ -d "$PROJECT_ROOT/backend" ]; then
        log_info "Building backend image..."
        cd "$PROJECT_ROOT/backend"
        docker build -t todo-backend:latest .
        minikube image load todo-backend:latest -p "$MINIKUBE_PROFILE"
    else
        log_warning "Backend directory not found, skipping backend build"
    fi
    
    # Build frontend image
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        log_info "Building frontend image..."
        cd "$PROJECT_ROOT/frontend"
        docker build -t todo-frontend:latest .
        minikube image load todo-frontend:latest -p "$MINIKUBE_PROFILE"
    else
        log_warning "Frontend directory not found, skipping frontend build"
    fi
    
    # Deploy using Helm
    log_info "Deploying application with Helm..."
    helm upgrade --install todo-app "$PROJECT_ROOT/charts/todo-app" \
        --namespace "$NAMESPACE" \
        --set backend.image.repository=todo-backend \
        --set backend.image.tag=latest \
        --set frontend.image.repository=todo-frontend \
        --set frontend.image.tag=latest \
        --wait --timeout 10m
    
    log_success "Application deployed"
}

install_monitoring() {
    log_info "Installing monitoring stack..."
    
    # Add Helm repositories
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/prometheus \
        --namespace "$NAMESPACE" \
        --set alertmanager.persistentVolume.size=2Gi \
        --set server.persistentVolume.size=5Gi \
        --set server.service.type=ClusterIP \
        --wait --timeout 5m
    
    # Install Grafana
    helm upgrade --install grafana grafana/grafana \
        --namespace "$NAMESPACE" \
        --set adminPassword=admin123 \
        --set service.type=ClusterIP \
        --wait --timeout 3m
    
    # Install Jaeger
    helm upgrade --install jaeger jaegertracing/jaeger \
        --namespace "$NAMESPACE" \
        --set provisionDataStore.cassandra=false \
        --set storage.type=memory \
        --wait --timeout 3m
    
    log_success "Monitoring stack installed"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    echo ""
    log_info "=== Namespace ==="
    kubectl get namespace "$NAMESPACE"
    
    echo ""
    log_info "=== Pods ==="
    kubectl get pods -n "$NAMESPACE"
    
    echo ""
    log_info "=== Services ==="
    kubectl get svc -n "$NAMESPACE"
    
    echo ""
    log_info "=== Dapr Components ==="
    dapr components -k
    
    echo ""
    log_info "=== Dapr Sidecars ==="
    kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.annotations.dapr\.io/app-id}{"\n"}{end}'
    
    echo ""
    log_info "=== Deployment Status ==="
    kubectl get deployments -n "$NAMESPACE"
    
    echo ""
    log_success "Deployment verification complete"
}

show_access_info() {
    echo ""
    log_success "========================================="
    log_success "Phase IV Deployment Complete!"
    log_success "========================================="
    echo ""
    log_info "Application URLs:"
    log_info "  Frontend: http://$(minikube ip -p "$MINIKUBE_PROFILE"):$(kubectl get svc frontend -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')"
    log_info "  Backend:  http://$(minikube ip -p "$MINIKUBE_PROFILE"):$(kubectl get svc backend -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')/health"
    echo ""
    log_info "Monitoring URLs:"
    log_info "  Grafana:    kubectl port-forward svc/grafana -n $NAMESPACE 3000:80"
    log_info "              http://localhost:3000 (admin/admin123)"
    log_info "  Prometheus: kubectl port-forward svc/prometheus-server -n $NAMESPACE 9090:80"
    log_info "              http://localhost:9090"
    log_info "  Jaeger:     kubectl port-forward svc/jaeger-query -n $NAMESPACE 16686:16686"
    log_info "              http://localhost:16686"
    echo ""
    log_info "Useful commands:"
    log_info "  View logs:       kubectl logs -n $NAMESPACE -l app=backend -f"
    log_info "  View Dapr logs:  kubectl logs -n $NAMESPACE -l app=backend -c daprd -f"
    log_info "  Exec into pod:   kubectl exec -n $NAMESPACE -it <pod-name> -- bash"
    log_info "  Port forward:    kubectl port-forward -n $NAMESPACE svc/backend 7860:7860"
    echo ""
}

# Main execution
main() {
    echo ""
    log_success "========================================="
    log_success "Phase IV: Todo App Deployment"
    log_success "========================================="
    echo ""
    
    check_prerequisites
    setup_minikube
    enable_addons
    install_dapr
    create_namespace
    install_kafka
    install_redis
    install_dapr_components
    build_and_deploy_app
    install_monitoring
    verify_deployment
    show_access_info
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
