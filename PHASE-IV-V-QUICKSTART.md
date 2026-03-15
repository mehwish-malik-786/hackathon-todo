# Phase IV & V - Quick Start Guide

**Last Updated**: 2026-03-14
**Status**: Ready for Implementation
**Estimated Time**: 2-3 hours for Phase IV, 4-6 hours for Phase V

---

## Overview

This guide provides a fast-track implementation path for Phase IV (Local Kubernetes) and Phase V (Cloud Production) based on the architecture decisions in ADR-001.

### Architecture Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cloud Provider | Azure AKS | Enterprise integration, cost-effective |
| Kafka (Local) | Bitnami Helm | Simple, reliable |
| Kafka (Prod) | Confluent Cloud | Managed, production-ready |
| State Backend | Redis + PostgreSQL | Speed + durability |
| Multi-Tenancy | Single-user, tenant-ready | Fast MVP, migration path |
| Monitoring | Prometheus + Grafana | Industry standard |
| Logging | Fluent Bit + Loki | Lightweight |
| CI/CD | GitHub Actions + GitOps | Automation first |

---

## Prerequisites

### Required Software
```bash
# Check installed versions
docker --version          # 20.x+
kubectl version --client  # 1.28+
helm version              # 3.x+
minikube version          # 1.32+
dapr --version            # 1.12+
```

### Install Missing Tools

#### macOS
```bash
brew install docker kubectl helm minikube dapr
```

#### Linux
```bash
# Docker
curl -fsSL https://get.docker.com | sh

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

#### Windows (WSL2)
```powershell
# Run in WSL2 terminal
choco install docker-desktop kubernetes-helm minikube dapr
```

---

## Phase IV: Local Kubernetes Implementation

### Step 1: Setup Minikube Cluster (10 min)

```bash
# Start Minikube with sufficient resources
minikube start \
  --cpus=4 \
  --memory=4096 \
  --disk-size=20gb \
  --driver=docker \
  --kubernetes-version=1.28.0

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
✓ minikube v1.32.0 on Ubuntu 22.04
✓ Kubernetes 1.28.0 is now available
✓ Started minikube
```

### Step 2: Enable Minikube Addons (5 min)

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics server
minikube addons enable metrics-server

# Enable storage provisioner
minikube addons enable storage-provisioner

# Verify addons
kubectl get pods -n ingress-nginx
kubectl get pods -n kube-system | grep metrics-server
```

### Step 3: Install Dapr Runtime (10 min)

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Wait for Dapr pods to be ready
kubectl wait --for=condition=ready pod -l app=dapr-dashboard -n dapr-system --timeout=120s
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=120s

# Verify Dapr installation
kubectl get pods -n dapr-system
dapr components -k
```

**Expected Output**:
```
NAME                                    READY   STATUS
dapr-dashboard-xxxxxxxxxx-xxxxx         1/1     Running
dapr-operator-xxxxxxxxxx-xxxxx          1/1     Running
dapr-placement-server-0                 1/1     Running
dapr-sentry-xxxxxxxxxx-xxxxx            1/1     Running
```

### Step 4: Create Namespace and RBAC (5 min)

```bash
# Apply namespace configuration
kubectl apply -f k8s/namespace.yaml

# Verify namespace
kubectl get namespace todo-dev
kubectl get resourcequota -n todo-dev
kubectl get limitrange -n todo-dev
```

### Step 5: Deploy Kafka (10 min)

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka (single replica for local dev)
helm install kafka bitnami/kafka \
  --namespace todo-dev \
  --set replicaCount=1 \
  --set persistence.size=5Gi \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=256Mi \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo-dev --timeout=300s

# Verify Kafka
kubectl get pods -n todo-dev | grep kafka
kubectl get svc -n todo-dev | grep kafka
```

### Step 6: Configure Dapr Pub/Sub Component (5 min)

Create `k8s/dapr-components/pubsub-kafka.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-dev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: 1048576
```

Apply the component:
```bash
kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml
```

### Step 7: Configure Dapr State Store (Redis) (5 min)

```bash
# Install Redis for Dapr state store
helm install redis bitnami/redis \
  --namespace todo-dev \
  --set architecture=standalone \
  --set auth.enabled=false \
  --set master.resources.requests.cpu=100m \
  --set master.resources.requests.memory=128Mi

# Wait for Redis
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n todo-dev --timeout=120s
```

Create `k8s/dapr-components/statestore-redis.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-dev
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

Apply:
```bash
kubectl apply -f k8s/dapr-components/statestore-redis.yaml
```

### Step 8: Build and Deploy Backend (15 min)

```bash
# Navigate to backend directory
cd backend

# Build Docker image
docker build -t todo-backend:latest .

# Load image into Minikube
minikube image load todo-backend:latest

# Deploy backend
kubectl apply -f ../k8s/backend-deployment.yaml

# Verify deployment
kubectl get pods -n todo-dev | grep backend
kubectl logs -n todo-dev -l app=backend -f
```

### Step 9: Build and Deploy Frontend (15 min)

```bash
# Navigate to frontend directory
cd frontend

# Build Docker image
docker build -t todo-frontend:latest .

# Load image into Minikube
minikube image load todo-frontend:latest

# Deploy frontend
kubectl apply -f ../k8s/frontend-deployment.yaml

# Verify deployment
kubectl get pods -n todo-dev | grep frontend
```

### Step 10: Access the Application (5 min)

```bash
# Get the application URL
minikube service frontend --url -n todo-dev

# Or use ingress (add to /etc/hosts)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access via browser
# http://todo.local
```

### Step 11: Install Observability Stack (15 min)

```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace todo-dev \
  --set alertmanager.persistentVolume.size=2Gi \
  --set server.persistentVolume.size=5Gi

# Install Grafana
helm install grafana grafana/grafana \
  --namespace todo-dev \
  --set adminPassword=admin123 \
  --set service.type=LoadBalancer

# Install Jaeger
helm install jaeger jaegertracing/jaeger \
  --namespace todo-dev \
  --set provisionDataStore.cassandra=false \
  --set storage.type=memory

# Access Grafana
kubectl port-forward svc/grafana 3000:80 -n todo-dev
# http://localhost:3000 (admin/admin123)
```

### Phase IV Completion Checklist

- [ ] Minikube cluster running
- [ ] Dapr runtime installed
- [ ] Kafka deployed and accessible
- [ ] Redis state store configured
- [ ] Backend service deployed
- [ ] Frontend service deployed
- [ ] Ingress accessible
- [ ] Prometheus metrics collecting
- [ ] Grafana dashboards working
- [ ] Jaeger tracing functional

**Total Time**: ~2 hours

---

## Phase V: Cloud Production (Azure AKS)

### Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Azure Kubernetes Service extension
az extension add --name aks-preview
az extension update --name aks-preview

# Login to Azure
az login

# Set subscription
az account set --subscription "<your-subscription-id>"
```

### Step 1: Create Azure Container Registry (5 min)

```bash
# Create resource group
az group create \
  --name todo-rg \
  --location eastus

# Create ACR
az acr create \
  --resource-group todo-rg \
  --name todoacr \
  --sku Basic \
  --admin-enabled true
```

### Step 2: Create AKS Cluster (20 min)

```bash
# Create AKS cluster
az aks create \
  --resource-group todo-rg \
  --name todo-aks \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --enable-addons monitoring \
  --enable-msi-auth-for-monitoring true

# Get credentials
az aks get-credentials \
  --resource-group todo-rg \
  --name todo-aks \
  --overwrite-existing

# Verify cluster
kubectl get nodes
```

### Step 3: Connect ACR to AKS (5 min)

```bash
# Attach ACR to AKS
az aks update \
  --resource-group todo-rg \
  --name todo-aks \
  --attach-acr todoacr

# Push images to ACR
docker tag todo-backend:latest todoacr.azurecr.io/todo-backend:latest
docker tag todo-frontend:latest todoacr.azurecr.io/todo-frontend:latest

az acr login --name todoacr
docker push todoacr.azurecr.io/todo-backend:latest
docker push todoacr.azurecr.io/todo-frontend:latest
```

### Step 4: Provision Confluent Cloud Kafka (15 min)

1. Go to [Confluent Cloud](https://confluent.cloud)
2. Create new cluster (Basic tier, ~$140/month)
3. Create API key for authentication
4. Get bootstrap servers endpoint

Create `k8s/dapr-components/pubsub-confluent.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-dev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "<confluent-bootstrap-server>:9092"
  - name: authType
    value: "saslPlaintext"
  - name: saslUsername
    secretKeyRef:
      name: confluent-secret
      key: api-key
  - name: saslPassword
    secretKeyRef:
      name: confluent-secret
      key: api-secret
```

Create secret:
```bash
kubectl create secret generic confluent-secret \
  --from-literal=api-key='<your-api-key>' \
  --from-literal=api-secret='<your-api-secret>' \
  -n todo-dev
```

### Step 5: Provision Azure Database for PostgreSQL (10 min)

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group todo-rg \
  --name todo-postgres \
  --admin-user azureuser \
  --admin-password '<secure-password>' \
  --sku-name Standard_B1ms \
  --version 15 \
  --location eastus

# Create database
az postgres flexible-server db create \
  --resource-group todo-rg \
  --server-name todo-postgres \
  --database-name todo-db
```

Create `k8s/dapr-components/statestore-postgres.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-dev
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connection-string
```

### Step 6: Deploy to AKS (10 min)

```bash
# Apply namespace
kubectl apply -f k8s/namespace.yaml

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Update Helm values for production
helm upgrade todo-app ./charts/todo-app \
  --namespace todo-dev \
  --f values-prod.yaml \
  --set image.repository=todoacr.azurecr.io/todo-backend \
  --set image.tag=latest \
  --set replicaCount=3 \
  --set resources.limits.cpu=1 \
  --set resources.limits.memory=1Gi

# Verify deployment
kubectl get pods -n todo-dev
kubectl get svc -n todo-dev
```

### Step 7: Setup Monitoring (Grafana Cloud) (15 min)

1. Sign up at [Grafana Cloud](https://grafana.com/products/cloud/)
2. Create stack
3. Get Prometheus endpoint and API key
4. Update Helm values

```yaml
# values-prod.yaml - Grafana Cloud config
grafanaCloud:
  enabled: true
  prometheusUrl: https://prometheus-prod-<id>.grafana.net/api/prom
  apiKey: <your-api-key>
```

### Step 8: Setup CI/CD Pipeline (30 min)

Create `.github/workflows/deploy-prod.yml`:

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to ACR
        uses: Azure/docker-login@v2
        with:
          login-server: todoacr.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push
        run: |
          docker build -t todoacr.azurecr.io/todo-backend:${{ github.ref_name }} .
          docker push todoacr.azurecr.io/todo-backend:${{ github.ref_name }}
      
      - name: Deploy to AKS
        uses: Azure/k8s-deploy@v4
        with:
          manifests: |
            k8s/backend-deployment.yaml
          images: |
            todoacr.azurecr.io/todo-backend:${{ github.ref_name }}
          namespace: todo-dev
```

### Phase V Completion Checklist

- [ ] AKS cluster running
- [ ] ACR configured and images pushed
- [ ] Confluent Cloud Kafka connected
- [ ] Azure PostgreSQL provisioned
- [ ] Dapr components configured for cloud
- [ ] Application deployed to AKS
- [ ] Grafana Cloud monitoring active
- [ ] CI/CD pipeline functional
- [ ] Production URL accessible
- [ ] Health checks passing

**Total Time**: ~3-4 hours

---

## Troubleshooting

### Common Issues

#### Minikube won't start
```bash
# Delete and recreate
minikube delete
minikube start --cpus=4 --memory=4096
```

#### Dapr pods not ready
```bash
# Check Dapr logs
kubectl logs -n dapr-system -l app=dapr-operator
# Reinstall Dapr
dapr uninstall -k
dapr init -k
```

#### Kafka connection issues
```bash
# Check Kafka broker
kubectl exec -it kafka-0 -n todo-dev -- kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

#### Image pull errors
```bash
# For Minikube, load image
minikube image load todo-backend:latest
# For AKS, check ACR credentials
kubectl get secret acr-secret -n todo-dev -o yaml
```

### Getting Help

- **Specs**: `specs/features/phase-iv-local-kubernetes.md`
- **Tasks**: `specs/features/phase-iv-tasks.md`
- **ADRs**: `history/adr/001-phase-iv-v-architecture-decisions.md`
- **Constitution**: `.specify/memory/phase-iv-v-constitution.md`

---

## Next Steps

After completing Phase IV-V:

1. **Implement Advanced Features** (PH5-FEATURE-* tasks)
   - Recurring tasks
   - Due dates and reminders
   - Search and filtering
   - Tags and priorities

2. **Optimize Performance**
   - HPA configuration
   - Database query optimization
   - Cache strategies

3. **Enhance Security**
   - OAuth2/OIDC integration
   - Rate limiting
   - Network policies

4. **Scale Testing**
   - Load testing with k6
   - Chaos engineering with Chaos Mesh
   - Performance benchmarking

---

**Estimated Total Cost**:
- Phase IV (Local): $0 (local resources)
- Phase V (Production): ~$300-500/month
  - AKS: ~$100/month (3 nodes)
  - Confluent Cloud: ~$140/month (Basic)
  - PostgreSQL: ~$50/month (Basic tier)
  - Grafana Cloud: ~$50/month (Pro tier)
  - ACR: ~$10/month
