#!/bin/bash
set -e

echo "=== RM SaaS Platform Startup ==="
echo "Python: $(python --version 2>&1)"
echo "PORT: ${PORT:-8000}"

echo ""
echo "=== Running Migrations ==="
python manage.py migrate --noinput

echo ""
echo "=== Creating Superuser (if not exists) ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
" || echo "Note: Superuser creation skipped"

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
