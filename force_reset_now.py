#!/usr/bin/env python
"""
FORCE RESET - Guaranteed execution
Deletes ALL old objects and loads 10 new ones
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from data.models import Obj, System, Atribute, Data
from django.core.management import call_command

print("="*60)
print("🔥 FORCE RESET - DELETING OLD DATA")
print("="*60)

# Delete everything
print("\n🗑️ Deleting old data...")
try:
    data_count = Data.objects.count()
    Data.objects.all().delete()
    print(f"✅ Deleted {data_count} Data records")
except Exception as e:
    print(f"⚠️ Data: {e}")

try:
    attr_count = Atribute.objects.count()
    Atribute.objects.all().delete()
    print(f"✅ Deleted {attr_count} Atribute records")
except Exception as e:
    print(f"⚠️ Atribute: {e}")

try:
    sys_count = System.objects.count()
    System.objects.all().delete()
    print(f"✅ Deleted {sys_count} System records")
except Exception as e:
    print(f"⚠️ System: {e}")

try:
    obj_count = Obj.objects.count()
    Obj.objects.all().delete()
    print(f"✅ Deleted {obj_count} Obj records")
except Exception as e:
    print(f"⚠️ Obj: {e}")

print("\n📊 Loading 10 quality objects...")
print("-"*60)

try:
    call_command('load_quality_demo')
    print("\n" + "="*60)
    print("✅ SUCCESS! NEW DATA LOADED")
    print("="*60)
    print(f"\n📊 Results:")
    print(f"   Objects: {Obj.objects.count()}")
    print(f"   Systems: {System.objects.count()}")
    print(f"   Sensors: {Atribute.objects.count()}")
    print(f"   Data points: {Data.objects.count()}")
    print(f"\n🌐 Check: https://www.promonitor.kz/dashboard/")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
