# 🎬 Phase IV Demo Video Guide

**Quick Reference for Demo Video Recording**

---

## ✅ Current Status (Ready for Demo)

| Component | Status | URL/Port |
|-----------|--------|----------|
| **Minikube Cluster** | ✅ Running | - |
| **Demo Application** | ✅ Running | http://192.168.49.2:30080 |
| **Namespace** | ✅ Created | todo-dev |
| **Backend Pods** | ⏳ Pending | - |
| **Frontend Pods** | ⏳ Pending | - |

---

## 🚀 Quick Demo Commands

### 1. Show Cluster Status
```bash
export PATH="/home/mehwish/hackathon-todo:$PATH"

# Show all pods in namespace
kubectl get pods -n todo-dev -o wide

# Show all services
kubectl get svc -n todo-dev

# Show deployments
kubectl get deployments -n todo-dev
```

### 2. Access Demo Application
```bash
# Open in browser
http://192.168.49.2:30080

# Or use minikube service command
minikube service todo-demo -n todo-dev --url
```

### 3. Show Application Details
```bash
# Describe demo deployment
kubectl describe deployment todo-demo -n todo-dev

# Show pod details
kubectl get pod -l app=todo-demo -n todo-dev -o wide
```

---

## 📹 Demo Video Script (Suggested Flow)

### Part 1: Introduction (30 seconds)
- Show terminal with project folder
- Mention: "Phase IV - Cloud-Native Kubernetes Deployment"

### Part 2: Infrastructure (1 minute)
```bash
# Show Minikube status
minikube status

# Show Kubernetes version
kubectl version --client
```

### Part 3: Deployment (1 minute)
```bash
# Show running pods
kubectl get pods -n todo-dev -o wide

# Highlight: Demo pods running successfully
```

### Part 4: Application Demo (2 minutes)
- Open browser: http://192.168.49.2:30080
- Show the demo page with:
  - ✅ Application Running status
  - Infrastructure components list
  - Architecture overview
  - Endpoints information

### Part 5: Kubernetes Features (1 minute)
```bash
# Show resource quotas
kubectl get resourcequota -n todo-dev

# Show service endpoints
kubectl get endpoints -n todo-dev
```

### Part 6: Conclusion (30 seconds)
- Summarize achievements
- Mention Phase V (Cloud Production) next steps

---

## 🔧 Full Deployment (If Needed)

If you want to show the complete backend/frontend deployment:

### Option A: Quick Setup (5 minutes)
```bash
export PATH="/home/mehwish/hackathon-todo:$PATH"
cd /home/mehwish/hackathon-todo

# Run the quick demo setup
./scripts/demo-video-quick.sh
```

### Option B: Full Production Setup (30-45 minutes)
```bash
export PATH="/home/mehwish/hackathon-todo:$PATH"
cd /home/mehwish/hackathon-todo

# Run complete deployment
./scripts/deploy-phase-iv.sh
```

---

## 📊 Key Metrics to Show

### Cluster Resources
```bash
kubectl top nodes
kubectl top pods -n todo-dev
```

### Service Information
```bash
kubectl get svc -n todo-dev -o wide
kubectl describe svc todo-demo -n todo-dev
```

### Network Policies
```bash
kubectl get networkpolicies -n todo-dev
```

---

## 🎯 Demo Highlights

### What's Working Now:
1. ✅ Minikube Kubernetes cluster
2. ✅ Namespace with resource quotas
3. ✅ Demo application running (nginx-based)
4. ✅ Service exposure via NodePort
5. ✅ ConfigMap for custom HTML

### What Can Be Added (Full Demo):
1. 🔄 Backend API (FastAPI + Python)
2. 🔄 Frontend UI (React/Next.js)
3. 🔄 Dapr service mesh
4. 🔄 Redis state store
5. 🔄 Kafka message queue

---

## 🌐 URLs for Demo

| Service | URL | Description |
|---------|-----|-------------|
| **Demo App** | http://192.168.49.2:30080 | Main demo page |
| **Minikube Dashboard** | `minikube dashboard` | Kubernetes UI |
| **Backend API** | Cluster-internal only | FastAPI backend |
| **Frontend** | Cluster-internal only | React frontend |

---

## 📝 Troubleshooting

### If demo page doesn't load:
```bash
# Check pod status
kubectl get pods -n todo-dev -l app=todo-demo

# Check service
kubectl get svc todo-demo -n todo-dev

# Restart deployment if needed
kubectl rollout restart deployment todo-demo -n todo-dev
```

### If Minikube stops:
```bash
minikube start --cpus=4 --memory=4096
```

---

## 🎬 Recording Tips

1. **Terminal Setup:**
   - Use dark theme for better visibility
   - Increase font size (14-16px)
   - Clear terminal before recording

2. **Browser Setup:**
   - Open demo page in fullscreen
   - Use browser dev tools to show network tab
   - Have multiple tabs ready (terminal, browser, docs)

3. **Audio:**
   - Speak clearly and slowly
   - Pause between sections
   - Explain technical terms briefly

4. **Visual Flow:**
   - Start with architecture diagram
   - Show code/manifests briefly
   - Demonstrate running application
   - End with summary

---

## 📋 Checklist Before Recording

- [ ] Minikube running
- [ ] Demo page accessible
- [ ] Terminal commands tested
- [ ] Browser page loaded
- [ ] Recording software ready
- [ ] Audio working
- [ ] Script/notes prepared

---

## 🎓 Key Talking Points

1. **Cloud-Native Architecture:**
   - Microservices design
   - Container orchestration
   - Service mesh (Dapr)

2. **Kubernetes Benefits:**
   - Auto-scaling (HPA)
   - Self-healing
   - Resource management

3. **Phase IV Achievements:**
   - Local Kubernetes cluster
   - Complete deployment automation
   - Production-ready manifests

4. **Phase V Vision:**
   - Azure AKS cloud deployment
   - Confluent Cloud Kafka
   - Grafana Cloud monitoring

---

**Last Updated:** 2026-03-15
**Status:** ✅ Ready for Demo Recording
