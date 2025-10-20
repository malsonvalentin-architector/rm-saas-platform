#!/usr/bin/env bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       ProMonitor.kz Web Service - Railway Deployment       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Определяем PORT с fallback на 8000
if [ -z "${PORT:-}" ]; then
    export PORT=8000
    echo "⚠️  PORT not set by Railway, using default: 8000"
else
    echo "✅ PORT from Railway: $PORT"
fi

echo ""
echo "📋 Environment:"
echo "   Python: $(python --version)"
echo "   Django: $(python -c 'import django; print(django.get_version())')"
echo "   Working Directory: $(pwd)"
echo "   PORT: $PORT"
echo ""

# Step 1: Migrations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/5: Database Migrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py migrate --noinput
echo "✅ Migrations completed"
echo ""

# Step 2: Create Superuser (NEW!)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/5: Creating Superuser"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username = 'admin';
email = 'admin@promonitor.kz';
password = 'ProMonitor2025!';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print('✅ Superuser created successfully!');
    print('   Username: admin');
    print('   Email: admin@promonitor.kz');
    print('   Password: ProMonitor2025!');
else:
    print('⚠️  Superuser already exists (skipping)');
" 2>&1 || echo "⚠️  Superuser creation warning (may already exist)"
echo ""

# Step 3: Static files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/5: Collecting Static Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py collectstatic --noinput --clear 2>&1 || echo "⚠️  collectstatic warning (non-critical)"
echo "✅ Static files ready"
echo ""

# Step 4: Verify ASGI
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4/5: Verifying ASGI Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -c "from rm.asgi import application; print('✅ ASGI application OK')"
echo ""

# Step 5: Start Daphne
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5/5: Starting Daphne ASGI Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Daphne starting on 0.0.0.0:$PORT"
echo ""

# Start Daphne with explicit port number (not variable)
exec daphne -b 0.0.0.0 -p $PORT -v 2 rm.asgi:application
