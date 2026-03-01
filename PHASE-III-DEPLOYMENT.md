# Phase III: Production Deployment Guide

## WSL Ubuntu + HuggingFace Spaces Deployment

Complete guide for deploying the AI Chatbot on WSL Ubuntu and HuggingFace Spaces.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [WSL Ubuntu Setup](#wsl-ubuntu-setup)
3. [Local Development](#local-development)
4. [HuggingFace Token Setup](#huggingface-token-setup)
5. [HuggingFace Spaces Deployment](#huggingface-spaces-deployment)
6. [Vercel Frontend Deployment](#vercel-frontend-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- [HuggingFace](https://huggingface.co/) account
- [Neon](https://neon.tech/) account (PostgreSQL database)
- [Vercel](https://vercel.com/) account (frontend hosting)

### System Requirements
- WSL Ubuntu 20.04+ on Windows
- Python 3.10+
- Node.js 18+
- Git

---

## WSL Ubuntu Setup

### 1. Install WSL (if not already installed)

```powershell
# From Windows PowerShell (Admin)
wsl --install -d Ubuntu
wsl --set-default Ubuntu
```

### 2. Update WSL Ubuntu

```bash
# Inside WSL terminal
sudo apt update && sudo apt upgrade -y
```

### 3. Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install system dependencies
sudo apt install -y \
    build-essential \
    libpq-dev \
    git \
    curl
```

### 4. Install Node.js

```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 5. Configure WSL Network (Important!)

WSL 2 uses NAT by default. For local testing:

```bash
# Add to ~/.bashrc
echo 'export HOST_IP=$(cat /etc/resolv.conf | grep "nameserver" | cut -f 2 -d " ")' >> ~/.bashrc
echo 'export NO_PROXY="localhost,127.0.0.1,$HOST_IP"' >> ~/.bashrc
source ~/.bashrc
```

---

## Local Development

### 1. Clone Repository

```bash
cd ~
git clone <your-repo-url>
cd hackathon-todo
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

### 3. Configure Environment

**backend/.env:**
```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host.db.neon.tech/dbname

# Local development alternative (SQLite)
# DATABASE_URL=sqlite:///todo.db

# API Configuration
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# HuggingFace API (Get token from: https://huggingface.co/settings/tokens)
HF_TOKEN=hf_your_token_here
HF_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
HF_API_TIMEOUT=30
```

### 4. Run Backend

```bash
# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

### 5. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

### 6. Test Locally

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task buy milk", "session_id": "test"}'

# Open in browser
# http://localhost:3000
# http://localhost:3000/chat
```

---

## HuggingFace Token Setup

### 1. Create HuggingFace Account

1. Go to https://huggingface.co/
2. Click "Sign Up"
3. Verify email

### 2. Generate API Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `hackathon-todo`
4. Type: **read** (writing not needed)
5. Copy token (starts with `hf_`)

### 3. Add Token to .env

```bash
# backend/.env
HF_TOKEN=hf_abcdefghijklmnopqrstuvwxyz123456
```

**Important:** Never commit `.env` to git!

---

## HuggingFace Spaces Deployment

### 1. Create Space

1. Go to https://huggingface.co/new-space
2. Space name: `hackathon-todo-backend`
3. License: MIT
4. Visibility: Public (or Private)
5. Click "Create Space"

### 2. Configure Space

1. Go to your Space settings
2. **Settings → Variables**
3. Add environment variables:

```
DATABASE_URL=postgresql://user:pass@host.db.neon.tech/dbname
API_URL=https://your-username-hackathon-todo-backend.hf.space
CORS_ORIGINS=https://your-username-hackathon-todo-frontend.vercel.app
HF_TOKEN=hf_your_token_here
HF_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
HF_API_TIMEOUT=30
TRANSFORMERS_CACHE=/tmp/transformers_cache
HF_HOME=/tmp/huggingface
```

### 3. Prepare Deployment Files

```bash
cd ~/hackathon-todo

# Ensure huggingface-deploy/ has all files:
# - Dockerfile.huggingface
# - requirements.txt
# - backend/ (all code)
```

### 4. Deploy to HuggingFace

**Option A: Using Git (Recommended)**

```bash
cd huggingface-deploy

# Initialize git (if not already)
git init
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/hackathon-todo-backend

# Add files
git add .
git commit -m "Phase III: Deploy AI chatbot with Qwen2.5"

# Push to HuggingFace
git push -u origin main
```

**Option B: Using HuggingFace Hub CLI**

```bash
# Install hub CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload files
huggingface-cli upload YOUR_USERNAME/hackathon-todo-backend ./huggingface-deploy .
```

### 5. Monitor Deployment

1. Go to your Space dashboard
2. Watch build logs
3. Wait for "Running" status (5-10 minutes)

### 6. Test Deployment

```bash
# Health check
curl https://your-username-hackathon-todo-backend.hf.space/health

# Test chat
curl -X POST https://your-username-hackathon-todo-backend.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task deployed test", "session_id": "hf-test"}'
```

---

## Vercel Frontend Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Configure Frontend

```bash
cd frontend

# Update vercel.json
cat > vercel.json << EOF
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-username-hackathon-todo-backend.hf.space"
  }
}
EOF
```

### 4. Deploy

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### 5. Update Backend CORS

1. Go to HuggingFace Space settings
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
3. Click "Factory Rebuild"

### 6. Test End-to-End

1. Open https://your-app.vercel.app/chat
2. Send message: "Add task test deployment"
3. Verify task created
4. Send: "Show my tasks"
5. Verify tasks listed

---

## Troubleshooting

### WSL Network Issues

**Problem:** Can't access localhost from Windows browser

**Solution:**
```bash
# In WSL, find your IP
hostname -I

# Use that IP instead of localhost
# e.g., http://172.28.160.1:8000
```

### HF_TOKEN Not Working

**Problem:** "Invalid token" error

**Solution:**
1. Verify token starts with `hf_`
2. Ensure token type is "read"
3. Regenerate token if needed
4. Restart Space after updating token

### Model Loading Slow

**Problem:** First request takes >1 minute

**Solution:**
- HuggingFace API mode: Model loads on HF side (fast)
- Local mode: Use smaller model or enable GPU in Space settings

### CORS Errors

**Problem:** "CORS policy blocked"

**Solution:**
1. Update `CORS_ORIGINS` in backend
2. Include both Vercel and localhost URLs
3. Rebuild HuggingFace Space
4. Redeploy Vercel frontend

### Database Connection Failed

**Problem:** "Cannot connect to database"

**Solution:**
```bash
# Test connection
psql $DATABASE_URL

# Check Neon dashboard
# Ensure database is active
# Verify connection string format
```

### Memory Issues on HuggingFace

**Problem:** "Out of memory" error

**Solution:**
1. Use HF Inference API (cloud) - no local model
2. Or upgrade to HuggingFace Pro (GPU)
3. Or use rule-based fallback only

---

## Production Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] `.env` configured correctly
- [ ] HF_TOKEN set and valid
- [ ] Database connection working
- [ ] CORS configured for production URLs

### Backend (HuggingFace)
- [ ] Space builds successfully
- [ ] Health check returns 200
- [ ] Chat API responds
- [ ] Model loads (or fallback works)
- [ ] Environment variables set

### Frontend (Vercel)
- [ ] Build succeeds
- [ ] `/chat` page accessible
- [ ] Backend connection works
- [ ] No console errors
- [ ] Mobile responsive

### Post-Deployment
- [ ] End-to-end chat functional
- [ ] Tasks persist to database
- [ ] Conversation history loads
- [ ] Error handling works
- [ ] Performance acceptable

---

## Performance Optimization

### HuggingFace API Mode (Recommended)

```bash
# No local model needed
# Fast responses (~500ms)
# No memory issues
# Free tier sufficient
```

### Local Model Mode (Fallback)

```bash
# Use INT8 quantization
# Limit context window
# Enable GPU in Space settings
# Cache model in /tmp
```

---

## Cost Estimation

### HuggingFace Free Tier
- **CPU:** 2 vCPU, 16GB RAM ✅ Sufficient
- **Storage:** 50GB ✅ Sufficient
- **Monthly Hours:** 500 hours ✅ Sufficient

### Vercel Free Tier
- **Bandwidth:** 100GB/month ✅ Sufficient
- **Serverless Functions:** 100GB-hours ✅ Sufficient
- **Preview Deployments:** Unlimited ✅

### Neon Free Tier
- **Storage:** 0.5 GB ✅ Sufficient for demo
- **Compute:** 0.25 vCPU ✅ Sufficient

**Total Monthly Cost: $0** (Free tiers)

---

## Security Best Practices

### Environment Variables
- ✅ Never commit `.env` to git
- ✅ Use HuggingFace Variables for secrets
- ✅ Use Vercel Environment Variables
- ✅ Rotate HF_TOKEN periodically

### Database
- ✅ Use strong password
- ✅ Enable IP allowlist (Neon)
- ✅ Use SSL connection
- ✅ Regular backups

### API
- ✅ CORS configured for specific origins
- ✅ Rate limiting (HF API has built-in)
- ✅ Input validation
- ✅ Error messages don't leak internals

---

## Monitoring

### Health Checks

```bash
# Backend health
curl https://your-space.hf.space/health

# Readiness check
curl https://your-space.hf.space/ready

# Chat health
curl https://your-space.hf.space/api/chat/health
```

### Logs

**HuggingFace:**
- Space dashboard → Logs
- Real-time streaming

**Vercel:**
- Dashboard → Deployments → Logs
- CLI: `vercel logs`

---

## Next Steps

After successful deployment:

1. **Monitor Usage:** Check HuggingFace dashboard
2. **Gather Feedback:** Test with real users
3. **Optimize:** Based on usage patterns
4. **Scale:** Upgrade resources if needed
5. **Phase IV:** Plan Kubernetes deployment

---

## References

- [HuggingFace Inference API Docs](https://huggingface.co/docs/api-inference)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [WSL 2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Neon Database Docs](https://neon.tech/docs)
- [Vercel Deployment](https://vercel.com/docs/deployments)

---

**Version:** 1.0.0
**Created:** 2026-02-28
**Last Updated:** 2026-02-28
**Status:** Production Ready
