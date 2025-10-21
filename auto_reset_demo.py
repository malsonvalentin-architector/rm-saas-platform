#!/usr/bin/env python
"""
Auto Reset Demo Data Script
Automatically clears and reloads demo data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from data.models import Obj, System, Atribute, Data
from django.core.management import call_command

def main():
    print("=" * 60)
    print("🚀 AUTO RESET DEMO DATA")
    print("=" * 60)
    print()
    
    # Clear old data
    print("🗑️  STEP 1: Clearing old demo data...")
    print("-" * 60)
    
    try:
        count = Data.objects.count()
        Data.objects.all().delete()
        print(f"✅ Deleted Data: {count} records")
    except Exception as e:
        print(f"⚠️  Data deletion: {e}")
    
    try:
        count = Atribute.objects.count()
        Atribute.objects.all().delete()
        print(f"✅ Deleted Atribute: {count} records")
    except Exception as e:
        print(f"⚠️  Atribute deletion: {e}")
    
    try:
        count = System.objects.count()
        System.objects.all().delete()
        print(f"✅ Deleted System: {count} records")
    except Exception as e:
        print(f"⚠️  System deletion: {e}")
    
    try:
        count = Obj.objects.count()
        Obj.objects.all().delete()
        print(f"✅ Deleted Obj: {count} records")
    except Exception as e:
        print(f"⚠️  Obj deletion: {e}")
    
    print()
    print("📊 STEP 2: Loading fresh demo data...")
    print("-" * 60)
    
    try:
        call_command('load_quality_demo')
        print()
        print("=" * 60)
        print("✅ DEMO DATA RESET COMPLETE!")
        print("=" * 60)
        print()
        print("📊 Results:")
        print(f"   Obj: {Obj.objects.count()}")
        print(f"   System: {System.objects.count()}")
        print(f"   Atribute: {Atribute.objects.count()}")
        print(f"   Data: {Data.objects.count()}")
        print()
        print("🌐 Check: https://www.promonitor.kz/data/objects/")
        print()
        return 0
    except Exception as e:
        print(f"❌ Error loading demo data: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
