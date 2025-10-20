#!/bin/bash
set -e  # Exit on any error
set -x  # Print each command before executing

echo "========================================"
echo "=== ProMonitor.kz Web Service START ==="
echo "========================================"
echo "Python: $(python --version)"
echo "Django: $(python -c 'import django; print(django.get_version())')"
echo "PORT: ${PORT}"
echo "PWD: $(pwd)"
echo ""

echo "=== Step 1: Running Migrations ==="
python manage.py migrate --noinput
echo "✅ Migrations completed"
echo ""

echo "=== Step 2: Collecting Static Files ==="
python manage.py collectstatic --noinput --clear || {
    echo "⚠️ collectstatic failed, continuing anyway..."
}
echo "✅ Static files collected"
echo ""

echo "=== Step 3: Testing ASGI Import ==="
python -c "from rm.asgi import application; print('✅ ASGI application imported successfully')"
echo ""

echo "=== Step 4: Starting Daphne on 0.0.0.0:${PORT} ==="
echo "Command: daphne -b 0.0.0.0 -p ${PORT} rm.asgi:application"
echo ""
exec daphne -b 0.0.0.0 -p ${PORT} rm.asgi:application
