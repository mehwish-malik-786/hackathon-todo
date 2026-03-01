# 🚀 Vercel Deployment - Easy Guide

## ✅ Setup Complete!

Aapka frontend already configured hai Hugging Face backend ke saath:
- **Backend URL**: https://momi-malik-hackathon-todo-backend.hf.space
- **Frontend**: Ready for Vercel deployment

---

## 📋 Deploy in 3 Steps (2 Minutes)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
cd frontend
vercel
```

**Bas! Ho gaya deploy!** 🎉

---

## 🔗 Backend CORS Update (Important!)

Aapka Hugging Face backend abhi sirf `localhost:3000` ko allow kar raha hai.

**Vercel frontend ko connect karne ke liye:**

### Option A: Update Hugging Face Backend (Recommended)

1. Hugging Face Space dashboard mein jao:
   - https://huggingface.co/spaces/momi-malik/hackathon-todo-backend

2. **Files → Edit `.env`**

3. CORS_ORIGINS update karo:
   ```
   CORS_ORIGINS=http://localhost:3000,https://YOUR-APP.vercel.app
   ```
   (Replace `YOUR-APP` with your actual Vercel URL jo deploy ke baad milega)

4. **Factory Rebuild** karo (Settings → Factory Rebuild)

### Option B: Environment Variable in Vercel

Deploy ke baad, Vercel dashboard mein:
1. Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL` = `https://momi-malik-hackathon-todo-backend.hf.space`
3. Redeploy: `vercel --prod`

---

## 🎯 Your URLs

| Service | URL |
|---------|-----|
| Backend (Hugging Face) | https://momi-malik-hackathon-todo-backend.hf.space |
| Frontend (Vercel) | https://momi-malik-hackathon-todo-frontend.vercel.app |
| API Docs | https://momi-malik-hackathon-todo-backend.hf.space/docs |

---

## ✅ Pre-Deployment Check

```bash
cd frontend
npm run build
```

Agar build successful ho (✅ Compiled successfully), toh deployment ready hai!

---

## 🛠️ Useful Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# Open in browser
vercel open
```

---

## ❓ Troubleshooting

### CORS Error
Backend `.env` mein CORS_ORIGINS update karo aur Hugging Face rebuild karo.

### API Not Working
Check backend URL:
```bash
curl https://momi-malik-hackathon-todo-backend.hf.space/health
```

### Build Fails
```bash
cd frontend
npm run build
# Check errors
```

---

## 🎉 Quick Deploy Command

```bash
cd frontend && vercel && vercel --prod
```

Deploy ke baad backend CORS update karna mat bhoolna!
