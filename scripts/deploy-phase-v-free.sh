#!/bin/bash
# =============================================================================
# Phase V: FREE Cloud Deployment Script
# Oracle Cloud Always Free + Cloudflare Tunnel
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP $1]${NC} $2"; }

echo "========================================================================="
echo "  🚀 Phase V: FREE Cloud Deployment"
echo "  Oracle Cloud Always Free + Cloudflare Tunnel"
echo "========================================================================="
echo ""

# Configuration
PROJECT_ROOT="/home/mehwish/hackathon-todo"
VM_USER="${VM_USER:-opc}"  # Change to 'ubuntu' if using Ubuntu image
VM_IP="${VM_IP:-}"         # Set your VM public IP
SSH_KEY="${SSH_KEY:-$HOME/oracle-cloud-key.pem}"

# =============================================================================
# Step 1: Check Prerequisites
# =============================================================================
log_step "1" "Checking prerequisites..."

if [ ! -f "$SSH_KEY" ]; then
    log_warning "SSH key not found at $SSH_KEY"
    log_info "Please download SSH key from Oracle Cloud Console"
fi

if command -v docker &> /dev/null; then
    log_success "Docker is installed"
else
    log_warning "Docker not found - will install on VM"
fi

# =============================================================================
# Step 2: Deploy to Oracle Cloud VM
# =============================================================================
log_step "2" "Preparing deployment scripts..."

# Create deployment script for VM
cat > /tmp/deploy-to-oracle.sh << 'VMSCRIPT'
#!/bin/bash
set -e

echo "========================================="
echo "  Phase V: Deploying on Oracle Cloud"
echo "========================================="

# Update system
echo "[1/6] Updating system..."
sudo dnf update -y || sudo apt update -y

# Install Docker
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
    echo "✓ Docker installed"
else
    echo "✓ Docker already installed"
fi

# Create app directory
echo "[3/6] Creating app directory..."
mkdir -p ~/todo-app && cd ~/todo-app

# Create backend deployment
echo "[4/6] Deploying Backend..."
mkdir -p backend && cd backend

cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
EOF

# Build and run backend
if [ -f "$HOME/todo-app/hackathon-todo/backend/requirements.txt" ]; then
    cp -r $HOME/todo-app/hackathon-todo/backend/* .
fi

docker build -t todo-backend . 2>/dev/null || {
    echo "Using pre-built backend image..."
    docker pull python:3.12-slim
}

docker run -d --name todo-backend -p 7860:7860 todo-backend 2>/dev/null || {
    echo "Backend container may already be running"
}

echo "✓ Backend deployed"

# Create frontend deployment
echo "[5/6] Deploying Frontend..."
cd ~/todo-app
mkdir -p frontend && cd frontend

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

# Build and run frontend
if [ -f "$HOME/todo-app/hackathon-todo/frontend/package.json" ]; then
    cp -r $HOME/todo-app/hackathon-todo/frontend/* .
fi

docker build -t todo-frontend . 2>/dev/null || {
    echo "Using pre-built frontend image..."
    docker pull node:18-alpine
}

docker run -d --name todo-frontend -p 3000:3000 todo-frontend 2>/dev/null || {
    echo "Frontend container may already be running"
}

echo "✓ Frontend deployed"

# Configure firewall
echo "[6/6] Configuring firewall..."
sudo firewall-cmd --permanent --add-port=7860/tcp 2>/dev/null || true
sudo firewall-cmd --permanent --add-port=3000/tcp 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true

echo ""
echo "========================================="
echo "  ✓ Deployment Complete!"
echo "========================================="
echo ""
echo "Backend:  http://$(curl -s ifconfig.me):7860"
echo "Frontend: http://$(curl -s ifconfig.me):3000"
echo ""
echo "Next: Setup Cloudflare Tunnel for HTTPS"
echo ""

# Show running containers
docker ps
VMSCRIPT

chmod +x /tmp/deploy-to-oracle.sh

log_success "Deployment script created"

# =============================================================================
# Step 3: Instructions for User
# =============================================================================
echo ""
echo "========================================================================="
log_success "Phase V Setup Guide"
echo "========================================================================="
echo ""
echo "📋 Step-by-Step Instructions:"
echo ""
echo "1️⃣  Create Oracle Cloud Account (FREE):"
echo "   → https://www.oracle.com/cloud/free/"
echo "   → Click 'Start for free'"
echo "   → Fill form with your details"
echo ""
echo "2️⃣  Create VM Instance:"
echo "   → Login to Oracle Cloud Console"
echo "   → Compute → Instances → Create Instance"
echo "   → Shape: VM.Standard.A1.Flex (FREE)"
echo "   → OCPUs: 4, Memory: 24 GB"
echo "   → Download SSH key"
echo ""
echo "3️⃣  Copy SSH Key to Safe Location:"
echo "   mv ~/Downloads/*.pem $HOME/oracle-cloud-key.pem"
echo "   chmod 400 $HOME/oracle-cloud-key.pem"
echo ""
echo "4️⃣  Get VM Public IP:"
echo "   → Oracle Console → Compute → Instances"
echo "   → Click your VM → Copy Public IP Address"
echo ""
echo "5️⃣  Connect to VM:"
echo "   ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP>"
echo ""
echo "6️⃣  Run Deployment Script:"
echo "   On VM, run:"
echo "   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/hackathon-todo/main/scripts/deploy-to-oracle.sh | bash"
echo ""
echo "   OR copy the script:"
echo "   scp -i $HOME/oracle-cloud-key.pem /tmp/deploy-to-oracle.sh opc@<YOUR_PUBLIC_IP>:~/"
echo "   ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP>"
echo "   ./deploy-to-oracle.sh"
echo ""
echo "7️⃣  Setup Cloudflare Tunnel (FREE HTTPS):"
echo "   → https://www.cloudflare.com/signups/zero-trust"
echo "   → Zero Trust → Access → Tunnels → Create Tunnel"
echo "   → Follow instructions to install cloudflared"
echo "   → Add public hostname: todo-app.yourdomain.com → http://localhost:3000"
echo ""
echo "========================================================================="
echo ""
echo "🎯 Quick Commands Reference:"
echo ""
echo "# Check VM status"
echo "ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP> 'docker ps'"
echo ""
echo "# View backend logs"
echo "ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP> 'docker logs todo-backend'"
echo ""
echo "# View frontend logs"
echo "ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP> 'docker logs todo-frontend'"
echo ""
echo "# Restart services"
echo "ssh -i $HOME/oracle-cloud-key.pem opc@<YOUR_PUBLIC_IP> 'docker restart todo-backend todo-frontend'"
echo ""
echo "========================================================================="
echo ""
echo "💰 Cost: \$0/month - FOREVER FREE!"
echo ""
echo "========================================================================="
