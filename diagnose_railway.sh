#!/bin/bash
# Диагностика проблемы на Railway

echo "🔍 RAILWAY DIAGNOSTICS"
echo "====================="
echo ""

echo "1️⃣ Checking Python syntax..."
python manage.py check --deploy 2>&1 | head -30

echo ""
echo "2️⃣ Checking database connection..."
python manage.py showmigrations 2>&1 | tail -10

echo ""
echo "3️⃣ Checking objects count..."
python manage.py shell << PYTHON
from data.models import Obj, System, Atribute, Data
print(f"Obj: {Obj.objects.count()}")
print(f"System: {System.objects.count()}")
print(f"Atribute: {Atribute.objects.count()}")
print(f"Data: {Data.objects.count()}")
PYTHON

echo ""
echo "4️⃣ Checking for orphaned objects..."
python manage.py shell << PYTHON
from data.models import Obj
orphaned = Obj.objects.filter(company__isnull=True)
print(f"Orphaned Obj (company=None): {orphaned.count()}")
for obj in orphaned[:5]:
    print(f"  - {obj.obj} (ID: {obj.id})")
PYTHON

echo ""
echo "✅ Diagnostics complete"
