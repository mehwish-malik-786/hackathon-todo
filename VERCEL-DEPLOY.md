# 🚀 Vercel Deployment - Hackathon TODO Frontend

## ✅ Pre-Deployment Checklist

Your frontend is **already configured** for Vercel. Just follow these steps:

---

## 📋 Step-by-Step Deployment (5 Minutes)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```
Choose your preferred login method (GitHub, GitLab, email).

### Step 3: Deploy Frontend
```bash
cd /home/mehwish/hackathon-todo/frontend
vercel
```

**That's it!** Your frontend will be deployed in ~2 minutes.

---

## 🔗 Connect Backend (After Frontend Deploy)

### Option A: Backend on Railway (Recommended)
1. Deploy backend to Railway
2. Get your Railway URL (e.g., `https://my-api.railway.app`)
3. Run in terminal:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter: https://my-api.railway.app
   ```
4. Redeploy:
   ```bash
   vercel --prod
   ```

### Option B: Backend on Hugging Face Spaces
1. Deploy backend to Hugging Face Spaces
2. Get your Space URL (e.g., `https://huggingface.co/spaces/username/my-api`)
3. Run:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter: https://huggingface.co/spaces/username/my-api
   ```
4. Redeploy:
   ```bash
   vercel --prod
   ```

### Option C: Local Backend (Testing Only)
- Frontend on Vercel **cannot** access `localhost:8000`
- You must deploy backend to Railway/Hugging Face first

---

## 🛠️ Useful Commands

```bash
# View deployment status
vercel ls

# View logs
vercel logs

# Deploy to production
vercel --prod

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL

# Pull environment variables locally
vercel env pull
```

---

## ⚙️ Configuration Files (Already Set Up)

### `vercel.json`
- Framework: Next.js 14
- Build command: `npm run build`
- Output directory: `.next`
- Region: US East (iad1)

### `next.config.js`
- Output: standalone (optimized for deployment)
- Dist directory: `.next`

---

## 🎯 Your Deployed URLs

After deployment, you'll get:
- **Preview URL**: `https://hackathon-todo-xxxx.vercel.app`
- **Production URL**: `https://hackathon-todo.vercel.app` (after `vercel --prod`)

---

## ❓ Troubleshooting

### Build Fails
```bash
# Check build locally first
cd frontend
npm run build
```

### API Calls Fail
1. Ensure backend is deployed and accessible
2. Set `NEXT_PUBLIC_API_URL` in Vercel dashboard
3. Check CORS settings on backend

### CORS Error
Update backend `backend/.env`:
```
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```
Then redeploy backend.

---

## 📁 Files Created for Vercel

✅ `frontend/vercel.json` - Vercel configuration  
✅ `frontend/.env.example` - Environment variables template  
✅ `frontend/next.config.js` - Updated for production  

**Your existing code is NOT modified.** Safe to deploy!

---

## 🎉 Quick Deploy Summary

```bash
# One-line deploy (if already logged in)
cd frontend && vercel && vercel --prod
```

Then set backend URL in Vercel dashboard → Settings → Environment Variables.
