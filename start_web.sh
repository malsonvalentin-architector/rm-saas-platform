#!/bin/bash
set -e

echo "=== ProMonitor.kz Web Service Startup ==="
echo "Python: $(python --version)"
echo "Django: $(python -c 'import django; print(django.get_version())')"
echo "PORT: ${PORT}"

echo ""
echo "=== Running Migrations ==="
python manage.py migrate --noinput

echo ""
echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput

echo ""
echo "=== Starting Daphne (ASGI) on 0.0.0.0:${PORT} ==="
exec daphne -b 0.0.0.0 -p ${PORT} rm.asgi:application
