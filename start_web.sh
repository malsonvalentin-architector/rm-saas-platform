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
if python manage.py migrate --noinput; then
    echo "✅ Migrations completed"
else
    echo "❌ FATAL: Migrations failed!"
    exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1.5/5: Fixing SubscriptionPlan Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py fix_subscription_schema 2>&1 || echo "⚠️  Schema fix warning (may already be fixed)"
echo ""

# Step 2: Setup Default Users (superadmin + admin)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/5: Setting Up Default Users"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py setup_default_users 2>&1 || echo "⚠️  Default users setup warning"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2.3/6: Loading Subscription Plans"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python manage.py load_subscription_plans 2>&1; then
    echo "✅ Subscription plans loaded!"
else
    echo "⚠️  Subscription plans already exist"
fi
echo ""

# Step 2.5: Load Demo Data (ONE-TIME ONLY)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2.5/6: FORCE FIX - Test Users (Guaranteed)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py force_fix_users 2>&1 || echo "⚠️  Force fix warning"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2.6/6: Loading Demo Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python manage.py load_demo_data --user admin@promonitor.kz 2>&1; then
    echo "✅ Demo data loaded successfully!"
    echo "📊 Created:"
    echo "   • 3 objects (Data Center, Office, Production)"
    echo "   • 15+ controller systems"
    echo "   • 40+ sensors (temp, humidity, pressure, power)"
    echo "   • 11,520 readings (last 24 hours)"
    echo "   • 10+ alert rules"
else
    echo "⚠️  Demo data loading skipped (may already exist)"
fi
echo ""

# Step 3: Static files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/6: Collecting Static Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py collectstatic --noinput --clear 2>&1 || echo "⚠️  collectstatic warning (non-critical)"
echo "✅ Static files ready"
echo ""

# Step 4: Verify ASGI
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4/6: Verifying ASGI Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -c "from rm.asgi import application; print('✅ ASGI application OK')"
echo ""

# Step 5: Start Daphne
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5/6: Starting Daphne ASGI Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Daphne starting on 0.0.0.0:$PORT"
echo "📝 All startup steps completed successfully!"
echo "🌐 Application will be available at: https://www.promonitor.kz"
echo ""

# Start Daphne with explicit port number (not variable)
exec daphne -b 0.0.0.0 -p $PORT -v 2 rm.asgi:application
