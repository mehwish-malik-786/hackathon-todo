# 🎬 Phase IV Demo - START HERE!

**Your Demo Video is Ready to Record!**

---

## ✅ Quick Start (2 Steps)

### Step 1: Run the Access Script
```bash
./scripts/demo-easy-access.sh
```

### Step 2: Open Browser
```
http://localhost:8080
```

**That's it!** You should see the Phase IV Demo page with:
- ✅ Green status: "Application Running on Kubernetes"
- Infrastructure components
- Architecture diagram
- Service endpoints

---

## 🎥 Recording Your Demo Video

### What You'll See on the Page:

1. **Title:** 🚀 Phase IV - Kubernetes Demo
2. **Status Badge:** ✅ Application Running on Kubernetes
3. **Infrastructure Components:**
   - Kubernetes Cluster
   - Dapr Service Mesh
   - Redis State Store
   - Namespace with ResourceQuota
4. **Architecture:**
   - Backend: FastAPI + SQLModel
   - Frontend: React
   - Message Queue: Kafka
5. **Demo Endpoints**

### Suggested Video Flow (5 minutes):

**1. Introduction (30 seconds)**
- Show terminal
- Run: `kubectl get pods -n todo-dev`
- Explain: "This is Phase IV - Cloud-Native Kubernetes Deployment"

**2. Show Application (2 minutes)**
- Open: http://localhost:8080
- Point out the green status badge
- Explain the infrastructure components

**3. Technical Details (2 minutes)**
- Show deployment: `kubectl describe deployment todo-demo -n todo-dev`
- Explain: 2 replicas, health checks, rolling updates

**4. Conclusion (1 minute)**
- Summarize achievements
- Mention Phase V (Azure AKS cloud deployment)

---

## 🔧 Commands for Your Demo

```bash
# Set PATH (add to ~/.bashrc for permanence)
export PATH="/home/mehwish/hackathon-todo:$PATH"

# Show all pods
kubectl get pods -n todo-dev -o wide

# Show services
kubectl get svc -n todo-dev

# Show deployment details
kubectl describe deployment todo-demo -n todo-dev

# Show resource quotas
kubectl get resourcequota -n todo-dev
```

---

## 🌐 Access URLs

| Method | URL | Notes |
|--------|-----|-------|
| **Port Forward** | http://localhost:8080 | ✅ **RECOMMENDED** |
| Minikube Service | `minikube service todo-demo -n todo-dev` | Opens browser |
| Direct IP | http://192.168.49.2:30080 | May timeout on some networks |

---

## ⚠️ Troubleshooting

### If page doesn't load:
```bash
# Restart port-forward
pkill -f 'kubectl port-forward'
./scripts/demo-easy-access.sh
```

### If Minikube is not running:
```bash
minikube start --cpus=4 --memory=4096
```

### Quick status check:
```bash
kubectl get pods -n todo-dev
```

---

## 📁 Helpful Files

| File | Purpose |
|------|---------|
| `DEMO-QUICK-REFERENCE.md` | Quick command cheat sheet |
| `DEMO-STATUS-REPORT.md` | Complete status report |
| `DEMO-VIDEO-GUIDE.md` | Detailed recording guide |
| `scripts/demo-easy-access.sh` | Easy access script |

---

## ✅ Pre-Recording Checklist

- [ ] Run `./scripts/demo-easy-access.sh`
- [ ] Open http://localhost:8080 in browser
- [ ] Page shows green status badge
- [ ] Recording software ready
- [ ] Audio working
- [ ] Script/notes visible

---

## 🎯 Key Points to Mention

1. **Phase IV Achievement:**
   - Local Kubernetes cluster with Minikube
   - Containerized application deployment
   - Service exposure and networking

2. **Technical Features:**
   - 2 replicas for high availability
   - Health checks (liveness/readiness probes)
   - Resource limits (CPU/memory)
   - Rolling update strategy

3. **Phase V Vision:**
   - Azure AKS cloud deployment
   - Production-grade monitoring
   - Confluent Cloud Kafka
   - Grafana Cloud

---

## 🎬 Recording Tips

- **Terminal:** Use dark theme, large font (14-16px)
- **Browser:** Fullscreen mode for demo page
- **Audio:** Speak clearly, pause between sections
- **Pacing:** Take your time, don't rush

---

**Good Luck with Your Demo Video! 🚀🎥**

**Status:** ✅ Everything is ready!

**Access URL:** http://localhost:8080
