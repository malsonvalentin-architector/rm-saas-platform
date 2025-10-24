#!/bin/bash
set -e

echo "=== RM SaaS Platform Startup ==="
echo "Python: $(python --version 2>&1)"
echo "PORT: ${PORT:-8000}"

echo ""
echo "=== Running Migrations ==="
python manage.py migrate --noinput

echo ""
echo "=== Creating Superuser ==="
python manage.py create_superuser

echo ""
echo "=== Creating Demo Users ==="
python manage.py create_demo_users || echo "⚠️  Demo users creation failed, continuing..."

echo ""
echo "=== Setting up Enhanced Emulator Integration ==="
python manage.py setup_enhanced_emulator || echo "⚠️  Enhanced Emulator setup failed, continuing..."

echo ""
echo "=== Starting Gunicorn on 0.0.0.0:${PORT:-8000} ==="
exec gunicorn rm.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
