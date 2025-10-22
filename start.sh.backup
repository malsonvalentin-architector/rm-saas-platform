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
echo "=== Starting Gunicorn on 0.0.0.0:${PORT:-8000} ==="
exec gunicorn rm.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
