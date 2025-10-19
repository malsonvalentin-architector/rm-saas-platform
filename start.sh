#!/bin/bash
set -e

echo "=== RM SaaS Platform Startup ==="
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"
echo "PORT: ${PORT:-8000}"

echo ""
echo "=== Running App Check ==="
python manage.py check_app

echo ""
echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput --clear || echo "Static files collection failed, continuing..."

echo ""
echo "=== Running Migrations ==="
python manage.py migrate --noinput

echo ""
echo "=== Starting Gunicorn ==="
exec gunicorn rm.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance
