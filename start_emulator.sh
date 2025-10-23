#!/usr/bin/env bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Enhanced Emulator v2.0 - Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Environment:"
echo "   Python: $(python --version)"
echo "   Working Directory: $(pwd)"
echo ""

# Проверка файла emulator
if [ ! -f "modbus_emulator.py" ]; then
    echo "❌ FATAL: modbus_emulator.py not found!"
    exit 1
fi

echo "✅ Found modbus_emulator.py"
echo ""

# Проверка pymodbus
echo "🔍 Checking pymodbus installation..."
python -c "import pymodbus; print(f'✅ pymodbus version: {pymodbus.__version__}')" 2>&1 || {
    echo "❌ FATAL: pymodbus not installed!"
    echo "📦 Installing pymodbus..."
    pip install pymodbus==3.5.4
}
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Enhanced Emulator v2.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Listening on: 0.0.0.0:5020"
echo "🔧 Protocol: Modbus TCP"
echo "📊 Sensors: 12 total"
echo "🔄 Update interval: 5 seconds"
echo ""

# Запуск emulator
exec python modbus_emulator.py
