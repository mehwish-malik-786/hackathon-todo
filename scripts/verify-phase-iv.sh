#!/bin/bash
# =============================================================================
# Phase IV: Deployment Verification Script
# Description: Verify all Phase IV components are running correctly
# Usage: ./scripts/verify-phase-iv.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="todo-dev"
PASSED=0
FAILED=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_namespace() {
    log_info "Checking namespace $NAMESPACE..."
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_success "Namespace exists"
    else
        log_error "Namespace not found"
    fi
}

check_pods() {
    log_info "Checking pods in namespace $NAMESPACE..."
    
    local pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    
    if [ "$pods" -gt 0 ]; then
        log_success "Found $pods pods"
        
        # Check each pod status
        kubectl get pods -n "$NAMESPACE" --no-headers | while read -r line; do
            local pod_name=$(echo "$line" | awk '{print $1}')
            local ready=$(echo "$line" | awk '{print $2}')
            local status=$(echo "$line" | awk '{print $3}')
            
            if [ "$status" == "Running" ]; then
                log_success "Pod $pod_name: $ready - $status"
            else
                log_error "Pod $pod_name: $ready - $status"
            fi
        done
    else
        log_error "No pods found in namespace"
    fi
}

check_dapr() {
    log_info "Checking Dapr installation..."
    
    # Check Dapr system pods
    if kubectl get namespace dapr-system &> /dev/null; then
        log_success "Dapr system namespace exists"
        
        local dapr_pods=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
        if [ "$dapr_pods" -gt 0 ]; then
            log_success "Found $dapr_pods Dapr system pods"
        else
            log_error "No Dapr system pods found"
        fi
    else
        log_error "Dapr system namespace not found"
    fi
    
    # Check Dapr components
    log_info "Checking Dapr components..."
    local components=$(dapr components -k 2>/dev/null | grep -c "todo-" || true)
    if [ "$components" -gt 0 ]; then
        log_success "Found $components Dapr components in $NAMESPACE"
    else
        log_warning "No Dapr components found (may need to deploy app first)"
    fi
}

check_kafka() {
    log_info "Checking Kafka..."
    
    local kafka_pods=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka --no-headers 2>/dev/null | wc -l)
    if [ "$kafka_pods" -gt 0 ]; then
        local status=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        if [ "$status" == "Running" ]; then
            log_success "Kafka is running"
        else
            log_error "Kafka status: $status"
        fi
    else
        log_warning "Kafka not found (may need to install)"
    fi
}

check_redis() {
    log_info "Checking Redis..."
    
    local redis_pods=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=redis --no-headers 2>/dev/null | wc -l)
    if [ "$redis_pods" -gt 0 ]; then
        local status=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=redis -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        if [ "$status" == "Running" ]; then
            log_success "Redis is running"
        else
            log_error "Redis status: $status"
        fi
    else
        log_warning "Redis not found (may need to install)"
    fi
}

check_services() {
    log_info "Checking services..."
    
    local services=$(kubectl get svc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [ "$services" -gt 0 ]; then
        log_success "Found $services services"
        kubectl get svc -n "$NAMESPACE" --no-headers | while read -r line; do
            local svc_name=$(echo "$line" | awk '{print $1}')
            local svc_type=$(echo "$line" | awk '{print $2}')
            local svc_ports=$(echo "$line" | awk '{print $5}')
            log_info "  Service: $svc_name ($svc_type) - $svc_ports"
        done
    else
        log_warning "No services found"
    fi
}

check_monitoring() {
    log_info "Checking monitoring stack..."
    
    # Check Prometheus
    local prometheus=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=prometheus --no-headers 2>/dev/null | wc -l)
    if [ "$prometheus" -gt 0 ]; then
        log_success "Prometheus is installed"
    else
        log_warning "Prometheus not found"
    fi
    
    # Check Grafana
    local grafana=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=grafana --no-headers 2>/dev/null | wc -l)
    if [ "$grafana" -gt 0 ]; then
        log_success "Grafana is installed"
    else
        log_warning "Grafana not found"
    fi
    
    # Check Jaeger
    local jaeger=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=jaeger --no-headers 2>/dev/null | wc -l)
    if [ "$jaeger" -gt 0 ]; then
        log_success "Jaeger is installed"
    else
        log_warning "Jaeger not found"
    fi
}

check_helm_releases() {
    log_info "Checking Helm releases..."
    
    local releases=$(helm list -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [ "$releases" -gt 0 ]; then
        log_success "Found $releases Helm releases"
        helm list -n "$NAMESPACE" --no-headers | while read -r line; do
            local name=$(echo "$line" | awk '{print $1}')
            local chart=$(echo "$line" | awk '{print $2}')
            local status=$(echo "$line" | awk '{print $3}')
            log_info "  Release: $name ($chart) - $status"
        done
    else
        log_warning "No Helm releases found"
    fi
}

show_summary() {
    echo ""
    echo "========================================="
    echo "Verification Summary"
    echo "========================================="
    echo -e "${GREEN}Passed:${NC} $PASSED"
    echo -e "${RED}Failed:${NC} $FAILED"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All checks passed!${NC}"
        echo ""
        echo "Next steps:"
        echo "  - Access frontend: kubectl port-forward svc/frontend -n $NAMESPACE 3000:3000"
        echo "  - View Grafana:    kubectl port-forward svc/grafana -n $NAMESPACE 3000:80"
        echo "  - View logs:       kubectl logs -n $NAMESPACE -l app=backend -f"
    else
        echo -e "${RED}Some checks failed. Please review the errors above.${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  - Run deployment: ./scripts/deploy-phase-iv.sh"
        echo "  - Check pod logs: kubectl logs -n $NAMESPACE <pod-name>"
        echo "  - Describe pod:   kubectl describe pod -n $NAMESPACE <pod-name>"
    fi
    echo ""
}

# Main
main() {
    echo ""
    echo "========================================="
    echo "Phase IV Deployment Verification"
    echo "========================================="
    echo ""
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl not found${NC}"
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    check_namespace
    check_pods
    check_dapr
    check_kafka
    check_redis
    check_services
    check_monitoring
    check_helm_releases
    show_summary
}

main "$@"
