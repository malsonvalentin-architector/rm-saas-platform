#!/usr/bin/env bash
set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error
set -o pipefail  # Catch errors in pipes

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       ProMonitor.kz Web Service - Railway Deployment       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Environment info
echo "📋 Environment Information:"
echo "   Python: $(python --version 2>&1)"
echo "   Django: $(python -c 'import django; print(django.get_version())' 2>&1)"
echo "   Working Directory: $(pwd)"
echo "   PORT: ${PORT:-NOT_SET}"
echo "   DATABASE_URL: ${DATABASE_URL:0:30}... (truncated)"
echo "   REDIS_URL: ${REDIS_URL:0:30}... (truncated)"
echo ""

# Step 1: Database Migrations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/4: Running Database Migrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py migrate --noinput || {
    echo "❌ ERROR: Database migrations failed!"
    exit 1
}
echo "✅ Migrations completed successfully"
echo ""

# Step 2: Collect Static Files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/4: Collecting Static Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py collectstatic --noinput --clear 2>&1 || {
    echo "⚠️  WARNING: collectstatic failed, continuing anyway..."
}
echo "✅ Static files ready"
echo ""

# Step 3: Verify ASGI Application
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/4: Verifying ASGI Application Import"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -c "from rm.asgi import application; print('✅ ASGI application imported successfully')" || {
    echo "❌ ERROR: Cannot import rm.asgi:application"
    echo "This is CRITICAL - Daphne needs this to start!"
    exit 1
}
echo ""

# Step 4: Start Daphne ASGI Server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4/4: Starting Daphne ASGI Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Binding to: 0.0.0.0:${PORT}"
echo "ASGI Module: rm.asgi:application"
echo ""
echo "🚀 Starting Daphne..."
echo ""

# Use exec to replace the shell process with Daphne
# This ensures Daphne receives signals properly (SIGTERM, etc.)
exec daphne \
    --bind 0.0.0.0 \
    --port ${PORT} \
    --verbosity 2 \
    rm.asgi:application
