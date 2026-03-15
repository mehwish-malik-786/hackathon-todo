# 🎬 Phase IV Demo - Quick Reference Card

**Status:** ✅ **READY FOR VIDEO RECORDING**

---

## 🚀 One-Line Access (WORKING URL)

```
Demo URL: http://localhost:8080
```

**Note:** Port-forward must be running. Run: `./scripts/demo-easy-access.sh`

---

## 📋 5-Minute Setup

```bash
# 1. Set PATH
export PATH="/home/mehwish/hackathon-todo:$PATH"

# 2. Verify cluster
minikube status

# 3. Check pods
kubectl get pods -n todo-dev

# 4. Open browser
# http://192.168.49.2:30080
```

---

## 🎥 Demo Commands (Cheat Sheet)

| What to Show | Command |
|--------------|---------|
| **Cluster Status** | `minikube status` |
| **All Pods** | `kubectl get pods -n todo-dev -o wide` |
| **All Services** | `kubectl get svc -n todo-dev` |
| **Deployment Info** | `kubectl describe deployment todo-demo -n todo-dev` |
| **Resource Quotas** | `kubectl get resourcequota -n todo-dev` |
| **Events** | `kubectl get events -n todo-dev --sort-by='.lastTimestamp'` |

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Minikube | ✅ Running | Docker driver |
| Namespace | ✅ Active | todo-dev |
| Demo Pods | ✅ Running | 2/2 replicas |
| Demo Service | ✅ NodePort | Port 30080 |
| Demo Page | ✅ Working | Shows Phase IV info |

---

## 🎯 Demo Flow (5 Minutes)

1. **Terminal (2 min)**
   - Show `minikube status`
   - Show `kubectl get pods -n todo-dev`
   - Explain architecture

2. **Browser (2 min)**
   - Open http://192.168.49.2:30080
   - Point out features on page
   - Explain Kubernetes benefits

3. **Conclusion (1 min)**
   - Summarize achievements
   - Mention Phase V plans

---

## 🔧 Troubleshooting

```bash
# If page doesn't load
kubectl rollout restart deployment todo-demo -n todo-dev

# If Minikube stops
minikube start --cpus=4 --memory=4096

# Quick status check
kubectl get all -n todo-dev
```

---

## 📞 Key URLs

- **Demo Page:** http://192.168.49.2:30080
- **Health Check:** http://192.168.49.2:30080/health
- **Minikube Dashboard:** `minikube dashboard`

---

## ✅ Pre-Recording Checklist

- [ ] Terminal open with PATH set
- [ ] Browser tab ready for demo page
- [ ] Recording software running
- [ ] Audio working
- [ ] Script/notes visible

---

**Good Luck! 🎥🚀**
