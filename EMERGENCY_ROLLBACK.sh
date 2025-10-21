#!/bin/bash
# EMERGENCY ROLLBACK - Откат к последней рабочей версии

echo "🚨 EMERGENCY ROLLBACK INITIATED"
echo "Откатываемся к коммиту cd485bc (до багфикса AttributeError)"
echo ""

# Показать текущий статус
echo "=== Текущий коммит ==="
git log --oneline -1
echo ""

# Откат к последней рабочей версии
echo "=== Откатываемся к cd485bc ==="
git revert --no-edit 607cf3e 5e36a85 c362f7a

# Показать новый статус
echo ""
echo "=== После отката ==="
git log --oneline -3
echo ""

echo "✅ Rollback готов к push"
echo "Выполните: git push origin main"
