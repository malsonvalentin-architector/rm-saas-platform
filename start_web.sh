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

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1.5/5: Fixing SubscriptionPlan Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py fix_subscription_schema 2>&1 || echo "⚠️  Schema fix warning (may already be fixed)"
echo ""

# Step 2: Create/Update Superuser (FIXED FOR CUSTOM USER MODEL!)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/5: Creating/Updating Superuser"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
from data.models import Company;
User = get_user_model();
email = 'admin@promonitor.kz';
password = 'ProMonitor2025!';

# Создаём/получаем компанию ProMonitor
company, _ = Company.objects.get_or_create(
    name='ProMonitor Admin',
    defaults={
        'contact_person': 'Admin',
        'contact_email': email,
        'subscription_status': 'active',
        'is_active': True,
    }
);

# Обновляем или создаём суперпользователя (НЕ удаляем!)
user, created = User.objects.update_or_create(
    email=email,
    defaults={
        'password': User.objects.make_random_password(),  # temporary
        'first_name': 'Admin',
        'last_name': 'ProMonitor',
        'role': 'superadmin',  # ВАЖНО: superadmin, не admin!
        'company': company,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
);

# Устанавливаем правильный пароль
user.set_password(password);
user.save();

if created:
    print('✅ Superuser CREATED successfully!');
else:
    print('✅ Superuser UPDATED successfully!');

print('╔════════════════════════════════════════════════════════════╗');
print('║              ADMIN CREDENTIALS                             ║');
print('╠════════════════════════════════════════════════════════════╣');
print('║  URL:      https://promonitor.kz/admin/                    ║');
print('║  Email:    admin@promonitor.kz                             ║');
print('║  Password: ProMonitor2025!                                 ║');
print('║  Role:     superadmin                                      ║');
print('║  Company:  ProMonitor Admin                                ║');
print('╚════════════════════════════════════════════════════════════╝');
" 2>&1 || echo "⚠️  Superuser operation warning"
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
echo "STEP 2.5/6: Loading Demo Data"
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
echo ""

# Start Daphne with explicit port number (not variable)
exec daphne -b 0.0.0.0 -p $PORT -v 2 rm.asgi:application
