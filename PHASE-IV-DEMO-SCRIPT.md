# 🎬 Phase IV Demo Video Script

**Duration**: 5-7 minutes  
**Status**: ✅ Ready to Record  
**Date**: March 15, 2026

---

## 📋 Pre-Recording Checklist

- [x] Kubernetes cluster running (Kind)
- [x] Dapr installed in cluster
- [x] Redis deployed
- [x] Demo application running
- [x] All pods healthy

---

## 🎥 Scene 1: Introduction (30 seconds)

**Screen**: Terminal with project folder

**Script**:
> "Assalam-o-Alaikum! Today I'll demonstrate Phase IV of my TODO application - a cloud-native microservices architecture deployed on Kubernetes with Dapr service mesh."

**Commands to show**:
```bash
cd /home/mehwish/hackathon-todo
ls -la
```

---

## 🎥 Scene 2: Kubernetes Cluster Status (1 minute)

**Screen**: Terminal showing cluster info

**Script**:
> "First, let me show you our Kubernetes cluster. We're using Kind (Kubernetes in Docker) which is perfect for local development and testing."

**Commands**:
```bash
# Show cluster info
kubectl cluster-info

# Show nodes
kubectl get nodes

# Show Kubernetes version
kubectl version --short
```

**Expected Output**:
```
Kubernetes control plane is running at https://127.0.0.1:42067
CoreDNS is running at https://127.0.0.1:42067/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

NAME                 STATUS   ROLES           AGE    VERSION
kind-control-plane   Ready    control-plane   4d     v1.30.0
```

---

## 🎥 Scene 3: Namespace and Resources (1 minute)

**Screen**: Terminal showing namespace resources

**Script**:
> "Our application runs in the `todo-dev` namespace with proper resource quotas and limits. This ensures efficient resource utilization and isolation."

**Commands**:
```bash
# Show namespace
kubectl get namespace todo-dev

# Show all resources in namespace
kubectl get all -n todo-dev

# Show resource quota
kubectl get resourcequota -n todo-dev
```

**Highlight**:
- ✅ Redis running (state store)
- ✅ Demo application pods running
- ✅ ResourceQuota configured
- ✅ LimitRange for container limits

---

## 🎥 Scene 4: Dapr Service Mesh (1 minute)

**Screen**: Terminal showing Dapr components

**Script**:
> "Dapr provides our application with production-ready microservices building blocks including pub/sub messaging, state management, and service invocation."

**Commands**:
```bash
# Show Dapr pods
kubectl get pods -n dapr-system

# Show Dapr components
kubectl get components -n todo-dev

# Show Dapr configurations
kubectl get configurations -n todo-dev
```

**Expected Output**:
```
NAME                                     READY   STATUS
dapr-operator-xxxxxxxxxx                 1/1     Running
dapr-sentry-xxxxxxxxxx                   1/1     Running
dapr-placement-server-0                  1/1     Running
dapr-scheduler-server-x                  1/1     Running

NAME              AGE
todo-pubsub       12h
todo-statestore   12h
todo-secretstore  12h
```

---

## 🎥 Scene 5: Application Demo (1.5 minutes)

**Screen**: Split view - terminal + browser

**Script**:
> "Now let's access our application. The demo is running on port 30080 via NodePort service."

**Commands**:
```bash
# Show running pods
kubectl get pods -n todo-dev -l app=todo-demo

# Show services
kubectl get svc -n todo-dev todo-demo

# Test endpoint
kubectl run curl-test --image=curlimages/curl --rm -it -- curl -s http://todo-demo.todo-dev.svc.cluster.local
```

**Browser**: Open `http://localhost:30080` (if accessible)

**Show**:
- ✅ Application HTML page
- ✅ Infrastructure components listed
- ✅ Architecture overview

---

## 🎥 Scene 6: Redis State Store (1 minute)

**Screen**: Terminal showing Redis

**Script**:
> "Redis serves as our state store and cache. Let's verify it's running and accessible."

**Commands**:
```bash
# Show Redis pods
kubectl get pods -n todo-dev -l app.kubernetes.io/name=redis

# Show Redis service
kubectl get svc -n todo-dev | grep redis

# Test Redis connection
kubectl exec -it redis -- redis-cli ping
```

**Expected Output**:
```
redis                               1/1     Running
redis-master                        ClusterIP   10.96.115.0   6379/TCP
PONG
```

---

## 🎥 Scene 7: Architecture Overview (1 minute)

**Screen**: Show architecture diagram or slides

**Script**:
> "Let me summarize the architecture:
> 
> 1. **Frontend**: React application (to be deployed)
> 2. **Backend**: FastAPI microservice with SQLModel
> 3. **Dapr**: Service mesh for pub/sub and state management
> 4. **Redis**: State store and cache
> 5. **Kafka**: Message broker (via Dapr pub/sub)
> 6. **Kubernetes**: Container orchestration
> 
> This architecture is production-ready and follows cloud-native best practices."

**Show architecture**:
```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │
│  (React)    │     │  (FastAPI)  │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Dapr     │
                    │  Sidecar    │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
     │    Redis    │ │  Kafka  │ │  PostgreSQL │
     │ (State)     │ │ (Pub/Sub)│ │  (Persist)  │
     └─────────────┘ └─────────┘ └─────────────┘
```

---

## 🎥 Scene 8: Live Demo Commands (1 minute)

**Screen**: Terminal with live commands

**Script**:
> "Let me show you some live commands that demonstrate our application's capabilities."

**Commands**:
```bash
# Watch pods in real-time
kubectl get pods -n todo-dev -w

# Show deployment details
kubectl describe deployment todo-demo -n todo-dev

# Show logs
kubectl logs -n todo-dev todo-demo-xxxxxxxxx
```

**Highlight**:
- Real-time pod status
- Health checks working
- No restarts (stable)

---

## 🎥 Scene 9: Conclusion (30 seconds)

**Screen**: Terminal with summary

**Script**:
> "This completes our Phase IV demo. We have successfully deployed a cloud-native microservices application on Kubernetes with Dapr service mesh. The architecture is scalable, resilient, and production-ready.
> 
> Next steps include deploying the full backend and frontend applications, setting up monitoring with Prometheus and Grafana, and implementing CI/CD pipelines.
> 
> Thank you for watching!"

**Final Commands**:
```bash
# Quick status summary
kubectl get pods -n todo-dev
kubectl get pods -n dapr-system
echo "✅ Phase IV Demo Complete!"
```

---

## 🎬 Recording Tips

### Screen Setup
- **Resolution**: 1920x1080
- **Terminal Theme**: Dark (better for video)
- **Font Size**: 14-16pt (readable on video)
- **Terminal**: Full screen or split view

### Audio
- Speak clearly and slowly
- Pause between sections
- Use a quiet room

### Editing
- Add text overlays for key points
- Highlight important output
- Add transitions between scenes
- Include background music (optional)

### File Names for Recording
```
demo-video-part1-intro.mp4
demo-video-part2-cluster.mp4
demo-video-part3-namespace.mp4
demo-video-part4-dapr.mp4
demo-video-part5-app.mp4
demo-video-part6-redis.mp4
demo-video-part7-architecture.mp4
demo-video-part8-live.mp4
demo-video-part9-conclusion.mp4
```

---

## 📊 Key Metrics to Show

| Component | Status | Details |
|-----------|--------|---------|
| Kubernetes | ✅ Running | Kind v1.30.0 |
| Dapr | ✅ Running | v1.17.1 |
| Redis | ✅ Running | State store ready |
| Namespace | ✅ Created | todo-dev with quotas |
| Demo App | ✅ Running | 2 replicas, healthy |
| Services | ✅ Configured | NodePort 30080 |

---

## 🚀 Quick Demo Commands (Cheat Sheet)

```bash
# 1. Cluster status
kubectl cluster-info && kubectl get nodes

# 2. All pods
kubectl get pods -A | grep -E "todo-dev|dapr-system"

# 3. Demo app
kubectl get pods -n todo-dev -l app=todo-demo

# 4. Test app
kubectl run curl-test --image=curlimages/curl --rm -it -- curl -s http://todo-demo.todo-dev.svc.cluster.local

# 5. Redis
kubectl exec -it redis -n todo-dev -- redis-cli ping

# 6. Dapr
kubectl get components -n todo-dev

# 7. Summary
echo "=== Phase IV Demo Summary ===" && \
kubectl get pods -n todo-dev && \
kubectl get pods -n dapr-system && \
echo "✅ All systems operational!"
```

---

## ✅ Success Criteria

- [ ] All pods running without restarts
- [ ] Demo page accessible
- [ ] Redis responding to ping
- [ ] Dapr components configured
- [ ] Clear audio and video
- [ ] All commands execute without errors
- [ ] Total duration: 5-7 minutes

---

**Good Luck with your demo video! 🎉**
