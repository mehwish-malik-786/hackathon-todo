#!/bin/bash
# =============================================================================
# Demo Video - Easy Access Script
# Opens demo page in browser using port-forward
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/home/mehwish/hackathon-todo"
export PATH="$PROJECT_ROOT:$PATH"
NAMESPACE="todo-dev"

echo "========================================================================="
echo "  🎬 Phase IV Demo - Easy Access"
echo "========================================================================="
echo ""

# Check if minikube is running
if ! minikube status &>/dev/null; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=4096
fi

# Check if pods are running
echo -e "${BLUE}Checking demo pods...${NC}"
kubectl get pods -n $NAMESPACE -l app=todo-demo

echo ""
echo -e "${GREEN}✅ Demo is ready!${NC}"
echo ""
echo "========================================================================="
echo "  🌐 Access Options:"
echo "========================================================================="
echo ""
echo "  Option 1: Port Forward (Recommended)"
echo "  -------------------------------------"
echo "  URL: http://localhost:8080"
echo ""
echo "  This script will start port-forward in background."
echo ""
echo "  Option 2: Minikube Service Command"
echo "  -----------------------------------"
echo "  Run: minikube service todo-demo -n $NAMESPACE"
echo "  (Opens browser automatically)"
echo ""
echo "  Option 3: Direct IP (if network allows)"
echo "  ----------------------------------------"
echo "  URL: http://$(minikube ip):30080"
echo ""
echo "========================================================================="
echo ""

# Kill any existing port-forward
pkill -f "kubectl port-forward.*todo-demo" 2>/dev/null || true

# Start port-forward in background
echo -e "${BLUE}Starting port-forward on port 8080...${NC}"
kubectl port-forward svc/todo-demo -n $NAMESPACE 8080:80 --address=127.0.0.1 &
sleep 2

# Test connection
if curl -s http://localhost:8080 > /dev/null; then
    echo -e "${GREEN}✅ Port-forward is working!${NC}"
    echo ""
    echo "========================================================================="
    echo "  🎥 Ready for Demo Video!"
    echo "========================================================================="
    echo ""
    echo "  Open your browser and go to: http://localhost:8080"
    echo ""
    echo "  Port-forward is running in background."
    echo "  To stop it later: pkill -f 'kubectl port-forward'"
    echo ""
    echo "========================================================================="
else
    echo -e "${YELLOW}⚠️  Port-forward may need manual start${NC}"
    echo ""
    echo "Run this command:"
    echo "  kubectl port-forward svc/todo-demo -n $NAMESPACE 8080:80"
fi
