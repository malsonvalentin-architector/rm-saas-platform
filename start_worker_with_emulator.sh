#!/bin/bash
# Запуск Enhanced Emulator v2.0 + Celery Worker
# Используется Railway Worker service

echo "=========================================="
echo " Enhanced Emulator v2.0 + Worker Startup"
echo "=========================================="

# Запускаем Enhanced Emulator в фоне
echo "[1/2] Starting Enhanced Emulator v2.0..."
python modbus_emulator.py &
EMULATOR_PID=$!

# Ждём 3 секунды для инициализации эмулятора
sleep 3

# Проверяем, что эмулятор запустился
if ps -p $EMULATOR_PID > /dev/null; then
    echo "✓ Enhanced Emulator v2.0 started (PID: $EMULATOR_PID)"
    echo "  Listening on localhost:5020"
else
    echo "✗ Failed to start Enhanced Emulator"
    exit 1
fi

# Запускаем Celery Worker (основной процесс)
echo "[2/2] Starting Celery Worker..."
exec celery -A rm worker --loglevel=info --concurrency=2
