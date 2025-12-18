# Deployment Guide - AIT Search Engine

## Prerequisites
- Git repository pushed to GitHub
- All 59,540 documents indexed in `data/` folder
- Backend tested locally and working

---

## Option 1: Render (Recommended - Free Tier)

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Add deployment configurations"
git push origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `arslanali372006/AIT-Search`
4. Configure:
   - **Name**: `ait-search-engine`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd search_engine && python -m uvicorn app.backend.server:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**

### Step 3: Deploy Frontend
1. Click **"New +"** → **"Static Site"**
2. Connect same repository
3. Configure:
   - **Name**: `ait-search-frontend`
   - **Root Directory**: `search_engine/app/frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`
4. Update `script.js` API_BASE_URL to your backend URL:
   ```javascript
   const API_BASE_URL = 'https://ait-search-engine.onrender.com/api';
   ```
5. Push changes and redeploy

**Note**: Free tier sleeps after 15 min inactivity, first request takes ~30s to wake up.

---

## Option 2: Railway

### Step 1: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and deploy
5. Add environment variables:
   - Click on deployment → **Variables**
   - Add: `PORT=8000`
6. Your backend will be live at: `https://your-project.up.railway.app`

### Step 2: Update Frontend
1. Update `script.js` with Railway backend URL
2. Deploy frontend on Vercel/Netlify (see Option 3)

**Cost**: $5/month after free tier ($5 credit on signup)

---

## Option 3: Docker + Any Cloud (AWS, GCP, DigitalOcean)

### Step 1: Build Docker Image
```bash
cd /Users/arslanali/Documents/DSA_Project
docker build -f search_engine/deployment/dockerfile -t ait-search-engine .
```

### Step 2: Test Locally
```bash
docker-compose -f search_engine/deployment/docker-compose.yml up
```
Access at: http://localhost:8000

### Step 3: Deploy to Cloud
**For DigitalOcean App Platform:**
1. Push image to Docker Hub:
   ```bash
   docker tag ait-search-engine your-username/ait-search-engine
   docker push your-username/ait-search-engine
   ```
2. Go to DigitalOcean → **Apps** → **Create App**
3. Select Docker Hub and enter your image name
4. Set port to 8000
5. Deploy

**For AWS (Elastic Beanstalk):**
1. Install AWS CLI and EB CLI
2. Initialize:
   ```bash
   eb init -p docker ait-search-engine
   ```
3. Create environment:
   ```bash
   eb create ait-search-production
   ```
4. Deploy:
   ```bash
   eb deploy
   ```

---

## Option 4: Frontend Only on Vercel/Netlify

### Vercel (Frontend)
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure:
   - **Root Directory**: `search_engine/app/frontend`
   - **Build Command**: (none)
   - **Output Directory**: `.`
4. Before deploying, update backend URL in `script.js`
5. Deploy

### Netlify (Frontend)
1. Go to [netlify.com](https://netlify.com)
2. **Sites** → **Add new site** → **Import from Git**
3. Select repository
4. Configure:
   - **Base directory**: `search_engine/app/frontend`
   - **Build command**: (leave empty)
   - **Publish directory**: `.`
5. Update API URL and deploy

---

## Important Notes

### CORS Configuration
If frontend and backend are on different domains, update backend CORS:

```python
# In search_engine/app/backend/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://your-frontend-domain.vercel.app"  # Add your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Large Dataset Warning
⚠️ Your 59,540 documents with embeddings (~10GB data) may not fit on free tiers:
- **Render Free**: 512MB RAM, may crash
- **Railway**: 512MB RAM (free tier)
- **Vercel/Netlify**: Static sites only (no backend)

**Recommended for large dataset:**
- **Railway Pro**: $5/month, 8GB RAM
- **DigitalOcean**: $12/month droplet, 2GB RAM
- **AWS EC2 t3.small**: ~$15/month, 2GB RAM

### Environment Variables
Set these if needed:
- `PORT`: Server port (usually auto-set by platform)
- `EMBEDDINGS_DIR`: Path to embeddings (default: data/embeddings)
- `DATA_DIR`: Path to documents (default: data/)

---

## Testing Deployment

After deployment, test these endpoints:
- Health check: `https://your-backend/api/stats`
- Search: `https://your-backend/api/search/single?query=covid&top_k=10`
- Frontend: `https://your-frontend/`

---

## Quick Start (Render - Easiest)

```bash
# 1. Ensure everything is committed
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to render.com
# 3. New Web Service → Connect GitHub repo
# 4. Use the render.yaml configuration
# 5. Deploy and wait 5-10 minutes

# 6. Update frontend API URL
# Edit search_engine/app/frontend/script.js
# Change: const API_BASE_URL = 'https://your-app.onrender.com/api';

# 7. Deploy frontend as static site on Render
```

Your search engine will be live! 🚀
