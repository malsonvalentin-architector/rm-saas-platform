# Railway Deployment Setup Instructions

## ⚠️ IMPORTANT: Manual Configuration Required

Railway is ignoring both `Dockerfile CMD` and `Procfile` for the **web** service.
You MUST manually configure the Start Command through Railway UI.

### Step-by-Step Instructions:

#### For Web Service:
1. Open Railway Dashboard: https://railway.app/
2. Navigate to project: **adventurous-adventure**
3. Click on service: **web** (www.promonitor.kz)
4. Go to **Settings** tab
5. Scroll to **Deploy** section
6. Find **Start Command** field
7. Enter: `bash start_web.sh`
8. Click **Save** or **Redeploy**

#### For Worker Service:
1. Click on service: **worker**
2. Go to **Settings** → **Deploy**
3. Start Command: `celery -A rm worker --loglevel=info --concurrency=4`
4. Save

#### For Beat Service:
1. Click on service: **beat**
2. Go to **Settings** → **Deploy**
3. Start Command: `celery -A rm beat --loglevel=info`
4. Save

### Alternative: Use Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Link to project
railway link

# Set start commands
railway service --name web
railway up --detach
# Then in UI set: bash start_web.sh

railway service --name worker  
# Set: celery -A rm worker --loglevel=info --concurrency=4

railway service --name beat
# Set: celery -A rm beat --loglevel=info
```

### Expected Result:

After setting Start Commands, web service logs should show:

```
╔════════════════════════════════════════════════════════════╗
║       ProMonitor.kz Web Service - Railway Deployment       ║
╚════════════════════════════════════════════════════════════╝

✅ PORT from Railway: 8080

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1/4: Database Migrations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Migrations completed

... (steps 2-3) ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4/4: Starting Daphne ASGI Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Daphne starting on 0.0.0.0:8080

INFO     Listening on TCP address 0.0.0.0:8080
```

### Status After Setup:
- ✅ Web (Daphne ASGI): Running
- ✅ Worker (Celery): Running  
- ✅ Beat (Scheduler): Running
- ✅ Admin panel: https://www.promonitor.kz/admin/ (CSRF fixed)

### Notes:
- CSRF_TRUSTED_ORIGINS configured for admin access
- All services use correct commands from Procfile
- PostgreSQL and Redis connections working
