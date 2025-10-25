#!/bin/bash
# ============================================================================
# АВТОМАТИЧЕСКИЙ GIT PUSH ДЛЯ PHASE 4.4
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🚀 PUSH PHASE 4.4 НА GITHUB + RAILWAY DEPLOY         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /home/user/promonitor

echo "📋 Текущий статус:"
git status
echo ""

echo "📦 Коммиты для отправки:"
git log --oneline origin/main..HEAD
echo ""

echo "🔄 Выполняю git push..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ PUSH УСПЕШЕН!                             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Railway автоматически начнёт деплой через несколько секунд"
    echo "📍 Отслеживайте: https://railway.app/"
    echo ""
    echo "⏰ Ожидайте 5-7 минут, затем:"
    echo "   1. Выполните миграцию: python manage.py migrate"
    echo "   2. Создайте данные: python manage.py create_demo_actuators"
    echo "   3. Откройте: https://www.promonitor.kz/actuators/"
    echo ""
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    ❌ ОШИБКА PUSH                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Возможные причины:"
    echo "  1. Нужна аутентификация GitHub"
    echo "  2. Нет прав доступа к репозиторию"
    echo "  3. Проблемы с сетью"
    echo ""
    echo "Решение:"
    echo "  - Используйте GitHub Desktop"
    echo "  - Или настройте Git credentials"
    echo ""
fi
