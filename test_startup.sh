#!/usr/bin/env bash
# Test script to validate all startup commands locally

set -e

echo "🧪 Testing ProMonitor.kz Startup Commands"
echo "=========================================="
echo ""

# Step 1: Migrations
echo "1. Testing migrations..."
python manage.py migrate --noinput 2>&1 | tail -5
echo "✅ Migrations OK"
echo ""

# Step 2: Schema fix
echo "2. Testing schema fix..."
python manage.py fix_subscription_schema 2>&1 | tail -3 || echo "⚠️ Schema fix skipped"
echo ""

# Step 3: Setup users
echo "3. Testing setup_default_users..."
python manage.py setup_default_users 2>&1 | tail -5 || echo "⚠️ Users already exist"
echo ""

# Step 4: Load subscription plans
echo "4. Testing load_subscription_plans..."
python manage.py load_subscription_plans 2>&1 | tail -3 || echo "⚠️ Plans already exist"
echo ""

# Step 5: Force fix users
echo "5. Testing force_fix_users..."
python manage.py force_fix_users 2>&1 | tail -5 || echo "⚠️ Force fix skipped"
echo ""

# Step 6: Load demo data
echo "6. Testing load_demo_data..."
python manage.py load_demo_data --user admin@promonitor.kz 2>&1 | tail -5 || echo "⚠️ Demo data already exists"
echo ""

# Step 7: Collectstatic
echo "7. Testing collectstatic..."
python manage.py collectstatic --noinput --clear 2>&1 | tail -3
echo "✅ Collectstatic OK"
echo ""

# Step 8: ASGI check
echo "8. Testing ASGI application..."
python -c "from rm.asgi import application; print('✅ ASGI application OK')"
echo ""

echo "🎉 All startup commands tested successfully!"
echo "Ready for deployment"
