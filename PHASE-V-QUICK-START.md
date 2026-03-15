# 🚀 Phase V FREE - Quick Start Guide

**100% Free Cloud Deployment - No Payment Required!**

---

## ⚡ Quick Start (30 Minutes)

### Step 1: Oracle Cloud Account (10 min)

1. **Sign Up:** https://www.oracle.com/cloud/free/
2. **Click:** "Start for free"
3. **Fill in:**
   - Name, Email, Phone
   - Card details (for verification only - NO charges)
   - Upload ID if requested

**Note:** Oracle charges $1 for verification (refunded in 3-5 days)

---

### Step 2: Create Free VM (10 min)

1. **Login:** Oracle Cloud Console
2. **Go to:** Compute → Instances
3. **Click:** "Create Instance"

**Settings:**
```
Name: todo-app
Image: Oracle Linux 8 or Ubuntu 22.04
Shape: VM.Standard.A1.Flex ← IMPORTANT (This is FREE!)
OCPUs: 4
Memory: 24 GB
Public IPv4: YES ✓
SSH: Generate key pair (download it!)
```

4. **Click:** Create
5. **Wait:** 2-3 minutes

---

### Step 3: Connect & Deploy (10 min)

#### 3a: Get Your VM's Public IP
- Oracle Console → Instances → Click your VM
- Copy "Public IP Address" (e.g., 129.146.123.45)

#### 3b: Save SSH Key
```bash
# Move downloaded key to home folder
mv ~/Downloads/*.pem $HOME/oracle-cloud-key.pem
chmod 400 $HOME/oracle-cloud-key.pem
```

#### 3c: Connect to VM
```bash
# Replace with YOUR public IP
ssh -i $HOME/oracle-cloud-key.pem opc@129.146.123.45
```

**If using Ubuntu image:**
```bash
ssh -i $HOME/oracle-cloud-key.pem ubuntu@129.146.123.45
```

#### 3d: Run Deployment on VM
```bash
# Update system
sudo dnf update -y   # For Oracle Linux
# OR
sudo apt update -y   # For Ubuntu

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
```

#### 3e: Deploy Backend
```bash
# Create app directory
mkdir -p ~/todo-app/backend && cd ~/todo-app/backend

# Create simple backend (or clone your repo)
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Phase V - FREE Cloud Deployment!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/todos")
def get_todos():
    return [{"id": 1, "title": "Demo Todo", "completed": False}]
EOF

cat > requirements.txt << 'EOF'
fastapi
uvicorn
pydantic
EOF

cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
EOF

# Build and run
docker build -t todo-backend .
docker run -d --name todo-backend -p 7860:7860 todo-backend

# Test
curl http://localhost:7860/health
```

#### 3f: Deploy Frontend
```bash
cd ~/todo-app
mkdir -p frontend && cd frontend

# Simple frontend (or clone your repo)
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Phase V - FREE Cloud</title>
    <style>
        body { font-family: Arial; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        h1 { color: #667eea; }
        .status { background: #4caf50; color: white; padding: 15px 25px; border-radius: 8px; display: inline-block; margin: 20px 0; }
        .info { background: #e3f2fd; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #2196f3; }
        code { background: #f5f5f5; padding: 2px 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Phase V - FREE Cloud Deployment!</h1>
        <div class="status">✅ Running on Oracle Cloud (Free Tier)</div>
        
        <div class="info">
            <h2>Infrastructure</h2>
            <p><strong>Provider:</strong> Oracle Cloud Always Free</p>
            <p><strong>VM Shape:</strong> VM.Standard.A1.Flex</p>
            <p><strong>CPUs:</strong> 4 ARM</p>
            <p><strong>RAM:</strong> 24 GB</p>
            <p><strong>Cost:</strong> $0/month</p>
        </div>
        
        <div class="info">
            <h2>Endpoints</h2>
            <p><strong>Frontend:</strong> <code id="frontend-url">Loading...</code></p>
            <p><strong>Backend API:</strong> <code id="backend-url">Loading...</code></p>
        </div>
        
        <div class="info">
            <h2>API Test</h2>
            <button onclick="testAPI()" style="background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px;">Test Backend API</button>
            <pre id="api-response" style="background: #f5f5f5; padding: 15px; border-radius: 6px; margin-top: 15px; overflow: auto;"></pre>
        </div>
    </div>
    
    <script>
        // Get public IP
        fetch('https://api.ipify.org?format=json')
            .then(r => r.json())
            .then(data => {
                document.getElementById('frontend-url').textContent = 'http://' + data.ip + ':3000';
                document.getElementById('backend-url').textContent = 'http://' + data.ip + ':7860';
            });
        
        function testAPI() {
            fetch('/api/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('api-response').textContent = JSON.stringify(data, null, 2);
                })
                .catch(err => {
                    document.getElementById('api-response').textContent = 'Error: ' + err.message;
                });
        }
    </script>
</body>
</html>
EOF

cat > Dockerfile << 'EOF'
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
EOF

# Build and run
docker build -t todo-frontend .
docker run -d --name todo-frontend -p 3000:80 todo-frontend

# Test
curl http://localhost:3000
```

---

### Step 4: Setup Cloudflare Tunnel (10 min)

#### 4a: Create Cloudflare Account
1. Go to: https://www.cloudflare.com/
2. Sign up (free)
3. Verify email

#### 4b: Create Tunnel
1. **Dashboard:** Zero Trust → Access → Tunnels
2. **Click:** "Create a tunnel"
3. **Name:** todo-app
4. **Select:** Linux → amd64 (or arm64 if using ARM VM)
5. **Copy the token**

#### 4c: Install Cloudflared on VM
```bash
# SSH back into VM
ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP>

# Download cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Run tunnel (paste your token)
cloudflared tunnel --no-autoupdate run --token <YOUR_TOKEN_HERE>
```

#### 4d: Configure Public Hostname
1. In Cloudflare Tunnel dashboard
2. **Add Public Hostname:**
   - Subdomain: `todo-app`
   - Domain: `yourname.workers.dev` (free Cloudflare domain)
   - Service: `http://localhost:3000`
3. **Save**

---

## ✅ Final Result

**Your App is Live!**

```
https://todo-app.yourname.workers.dev
```

**Features:**
- ✅ FREE HTTPS
- ✅ Public URL
- ✅ Oracle Cloud hosting
- ✅ $0/month forever

---

## 🎬 Demo Video Script

### Show Oracle Console (1 min)
- Login → Compute → Instances
- Show VM running
- Highlight: "4 CPUs, 24GB RAM - FREE"

### Show SSH Connection (1 min)
```bash
ssh -i key.pem opc@<PUBLIC_IP>
docker ps
```

### Show Live App (2 min)
- Open: https://todo-app.yourname.workers.dev
- Test API
- Show it's accessible from anywhere

### Conclusion (30 sec)
- "Phase V complete - Production on Oracle Cloud"
- "Total cost: $0/month - Forever free!"

---

## 🆘 Troubleshooting

### Can't SSH to VM
```bash
# Check security list
Oracle Console → VCN → Security Lists → Default

# Add ingress rule:
Source: 0.0.0.0/0
Destination: All TCP Port 22
```

### Docker Won't Start
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Cloudflared Won't Connect
- Check token is correct (copy entire token)
- Ensure VM has internet access
- Try: `cloudflared --version`

---

## 📊 Resource Usage

| Resource | Free Limit | Your Usage |
|----------|------------|------------|
| CPUs | 4 ARM | ~1-2 used |
| RAM | 24 GB | ~2 GB used |
| Storage | 200 GB | ~5 GB used |
| **Cost** | **$0** | **$0** ✅ |

---

## ✅ Success Checklist

- [ ] Oracle Cloud account created
- [ ] VM instance running (VM.Standard.A1.Flex)
- [ ] Can SSH to VM
- [ ] Docker installed
- [ ] Backend running on port 7860
- [ ] Frontend running on port 3000
- [ ] Cloudflare tunnel active
- [ ] Public HTTPS URL working

---

**Status:** Ready to Deploy!  
**Cost:** $0/month Forever!  
**Time:** 30-60 minutes

🚀 **Let's go!**
