#!/usr/bin/env python
"""
Скрипт для загрузки демо данных актуаторов
Выполняется как Django management command
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')
django.setup()

# Import после setup
from django.core.management import call_command

print("=" * 70)
print("🚀 ЗАГРУЗКА ДЕМО ДАННЫХ ACTUATORS")
print("=" * 70)
print()

try:
    # Вызываем команду
    call_command('create_demo_actuators')
    print()
    print("=" * 70)
    print("✅ УСПЕШНО! Демо данные загружены!")
    print("=" * 70)
except Exception as e:
    print()
    print("=" * 70)
    print(f"❌ ОШИБКА: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
