# 🚀 Phase V - 100% FREE Cloud Deployment

**Zero Cost - Forever Free!**

---

## 🎯 Architecture (FREE Version)

```
┌─────────────────────────────────────────────────────────┐
│           Oracle Cloud Always Free                       │
│                                                          │
│   ┌────────────────┐    ┌────────────────┐              │
│   │   Backend      │    │   Frontend     │              │
│   │   (Docker)     │    │   (Docker)     │              │
│   │   FastAPI      │    │   Next.js      │              │
│   │   SQLite       │    │                │              │
│   └────────────────┘    └────────────────┘              │
│                                                          │
│   VM: 4 ARM CPUs + 24GB RAM (FREE Forever)              │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Cloudflare Tunnel    │ (FREE)
            │  Public HTTPS URL     │
            └───────────────────────┘
                        │
                        ▼
            🌐 Your Public URL:
            https://todo-app.yourdomain.com
```

---

## 💰 Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| **Oracle Cloud VM** | Always Free | **$0/month** |
| **Cloudflare Tunnel** | Free Plan | **$0/month** |
| **SQLite Database** | Built-in | **$0/month** |
| **Domain (Optional)** | Free subdomain | **$0/month** |
| **TOTAL** | | **$0/month** ✅ |

---

## 📋 Prerequisites

### What You Need (All Free):
1. **Oracle Cloud Account** - Sign up free
2. **Cloudflare Account** - Free plan
3. **GitHub Account** - For code
4. **Email** - For verification

### Time Required:
- Setup: **1-2 hours**
- Deployment: **30 minutes**
- Total: **~2 hours**

---

## 📝 Step-by-Step Guide

### Step 1: Oracle Cloud Account (10 minutes)

1. **Sign Up:** https://www.oracle.com/cloud/free/
2. **Click:** "Start for free"
3. **Fill form:**
   - Name, Email, Phone
   - Credit/Debit card (for verification only, NO charges)
   - Identity verification (upload ID if needed)

**Important:** Oracle does $1 verification charge (refunded immediately)

---

### Step 2: Create Free VM Instance (15 minutes)

1. **Login:** Oracle Cloud Console
2. **Navigate:** Compute → Instances
3. **Click:** "Create Instance"
4. **Configuration:**
   ```
   Name: todo-app-vm
   Compartment: Root compartment
   Availability Domain: Any (pick first)
   
   Image: Oracle Linux 8 or Ubuntu 22.04
   
   Shape: VM.Standard.A1.Flex (FREE)
   OCPUs: 4
   Memory: 24 GB
   
   Networking:
   - Virtual cloud network: Default
   - Subnet: Default
   - Assign public IPv4: ✓ YES
   
   SSH Keys:
   - Generate key pair (download private key)
   - Save as: oracle-cloud-key.pem
   
   Boot Volume:
   - Size: 50 GB (free tier limit)
   ```

5. **Click:** Create

**Wait 2-3 minutes for VM to be ready**

---

### Step 3: Connect to VM (10 minutes)

#### Option A: SSH from Your Computer
```bash
# Get Public IP from Oracle Console
# Navigate to: Compute → Instances → Click your VM → Copy Public IP

# Connect via SSH
ssh -i oracle-cloud-key-key opc@<YOUR_PUBLIC_IP>

# If using Ubuntu image:
ssh -i oracle-cloud-key-key ubuntu@<YOUR_PUBLIC_IP>
```

#### Option B: Cloud Shell (No SSH needed)
1. Click "Cloud Shell" icon (top right in Oracle Console)
2. Connect directly from browser

---

### Step 4: Install Docker on VM (10 minutes)

```bash
# Update system
sudo dnf update -y  # For Oracle Linux
# OR
sudo apt update -y  # For Ubuntu

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker run hello-world
```

---

### Step 5: Deploy Backend (15 minutes)

```bash
# Create app directory
mkdir -p ~/todo-app && cd ~/todo-app

# Clone your repository
git clone https://github.com/YOUR_USERNAME/hackathon-todo.git
cd hackathon-todo/backend

# Create Dockerfile (if not exists)
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
EOF

# Build Docker image
docker build -t todo-backend .

# Run container
docker run -d \
  --name todo-backend \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  todo-backend

# Check status
docker ps
curl http://localhost:7860/health
```

---

### Step 6: Deploy Frontend (15 minutes)

```bash
cd ~/todo-app/hackathon-todo/frontend

# Create Dockerfile (if not exists)
cat > Dockerfile << 'EOF'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "server.js"]
EOF

# Build Docker image
docker build -t todo-frontend .

# Run container
docker run -d \
  --name todo-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://<YOUR_PUBLIC_IP>:7860 \
  todo-frontend

# Check status
docker ps
curl http://localhost:3000
```

---

### Step 7: Setup Cloudflare Tunnel (20 minutes)

#### 7a: Create Cloudflare Account
1. Go to: https://www.cloudflare.com/
2. Sign up (free)
3. Verify email

#### 7b: Create Tunnel
1. **Dashboard:** Zero Trust → Access → Tunnels
2. **Click:** "Create a tunnel"
3. **Name:** todo-app-tunnel
4. **Select Environment:** Linux
5. **Select Architecture:** amd64 or arm64 (based on your VM)
6. **Copy the install command**

#### 7c: Install Cloudflared on VM
```bash
# Paste the command from Cloudflare dashboard
# It looks like:
# docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token <YOUR_TOKEN>

# Or install directly:
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Run tunnel
cloudflared tunnel --no-autoupdate run --token <YOUR_TOKEN>
```

#### 7d: Configure Public Hostname
1. In Cloudflare Tunnel dashboard
2. **Add Public Hostname:**
   - Subdomain: todo-app
   - Domain: yourdomain.com (or use free .tk domain)
   - Service: http://localhost:3000
3. **Save**

---

### Step 8: Access Your App (5 minutes)

**Your Public URL:**
```
https://todo-app.yourdomain.com
```

**Test from anywhere!**

---

## 🔧 Alternative: Free Domain Options

### Option 1: Free Subdomain (Recommended)
- Use Cloudflare's free subdomain
- URL: `todo-app.yourname.workers.dev`

### Option 2: Freenom Domain
- Get free .tk, .ml, .ga domain
- https://www.freenom.com/
- Connect to Cloudflare

### Option 3: DuckDNS
- Free dynamic DNS
- URL: `todo-app.duckdns.org`
- https://www.duckdns.org/

---

## 📊 Resource Limits (Free Tier)

| Resource | Oracle Free | Your Usage |
|----------|-------------|------------|
| CPUs | 4 ARM | ~30% used |
| RAM | 24 GB | ~2 GB used |
| Storage | 200 GB | ~5 GB used |
| Bandwidth | 10 TB/month | ~10 GB/month |
| **Cost** | **$0** | **$0** ✅ |

---

## 🎬 Demo Video Script (Phase V)

### Introduction (30 seconds)
"This is Phase V - Production Cloud Deployment on Oracle Cloud"

### Show Oracle Console (1 minute)
- Login to Oracle Cloud
- Show VM instance running
- Highlight: "4 CPUs, 24GB RAM - FREE"

### Show Deployment (2 minutes)
```bash
# SSH into VM
ssh -i key.pem opc@<PUBLIC_IP>

# Show running containers
docker ps

# Show logs
docker logs todo-backend
```

### Show Live App (1 minute)
- Open: https://todo-app.yourdomain.com
- Test creating a todo
- Show it persists

### Conclusion (30 seconds)
- "Phase V complete - Production deployment on Oracle Cloud"
- "Total cost: $0/month - Forever free!"

---

## ✅ Success Checklist

- [ ] Oracle Cloud account created
- [ ] VM instance running
- [ ] Docker installed
- [ ] Backend deployed (port 7860)
- [ ] Frontend deployed (port 3000)
- [ ] Cloudflare tunnel configured
- [ ] Public URL working
- [ ] App tested from different device

---

## 🆘 Troubleshooting

### VM Won't Start
- Check compartment permissions
- Try different availability domain
- Reduce shape to VM.Standard.E2.1.Micro

### Docker Installation Fails
```bash
# Check OS version
cat /etc/os-release

# For Oracle Linux:
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io
```

### Cloudflared Won't Connect
- Check token is correct
- Ensure firewall allows outbound connections
- Try Docker version instead

### Port Not Accessible
```bash
# Check firewall
sudo firewall-cmd --list-all

# Open ports if needed
sudo firewall-cmd --permanent --add-port=7860/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

---

## 📞 Support Resources

### Oracle Cloud
- Docs: https://docs.oracle.com/en-us/iaas/
- Free Tier: https://www.oracle.com/cloud/free/

### Cloudflare
- Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Community: https://community.cloudflare.com/

### Docker
- Docs: https://docs.docker.com/
- Hub: https://hub.docker.com/

---

## 🎯 Next Steps After Phase V

1. **Add Monitoring** (Free)
   - Uptime Kuma for uptime monitoring
   - Prometheus + Grafana for metrics

2. **Add CI/CD** (Free)
   - GitHub Actions for auto-deploy
   - Auto-build on git push

3. **Add Database** (Free)
   - PostgreSQL on same VM
   - Or use Supabase free tier

4. **Add Domain** (Optional)
   - Buy custom domain (~$10/year)
   - Or continue with free subdomain

---

**Status:** Ready to Deploy!  
**Cost:** $0/month Forever!  
**Time:** 1-2 hours setup

🚀 **Let's deploy Phase V for FREE!**
