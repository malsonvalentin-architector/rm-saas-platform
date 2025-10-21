#!/bin/bash
# Quick fix script for Railway deployment
# Run this via Railway CLI: railway run bash fix_demo_data.sh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    ProMonitor Demo Data Fix - Quick Reset                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "🗑️  Deleting old demo data and loading fresh..."
echo ""

python manage.py reset_demo_data --user admin@promonitor.kz --confirm

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ SUCCESS! Demo data has been reset                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Check results at: https://www.promonitor.kz/objects/"
    echo ""
    echo "📊 You should now see exactly 10 objects:"
    echo "   1. Дата-центр Алматы - Главный"
    echo "   2. Офисное здание на Абая"
    echo "   3. Производственный цех №1"
    echo "   4. Торговый центр Mega"
    echo "   5. Складской комплекс на Жандосова"
    echo "   6. Больничный комплекс"
    echo "   7. Гостиница Казжол"
    echo "   8. Бизнес-центр Нурлы Тау"
    echo "   9. Аптечный склад"
    echo "   10. Ресторан Рахат"
    echo ""
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ❌ ERROR! Something went wrong                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Check the error messages above"
    echo ""
fi
