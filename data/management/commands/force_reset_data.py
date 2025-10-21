#!/usr/bin/env python
"""
Management Command: force_reset_data

FORCE RESET - Guaranteed execution
Deletes ALL old objects and loads 10 new quality demo objects
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from data.models import Obj, System, Atributes, Data


class Command(BaseCommand):
    help = 'Force delete all objects and load 10 quality demo objects'

    def handle(self, *args, **options):
        self.stdout.write("="*60)
        self.stdout.write("🔥 FORCE RESET - DELETING OLD DATA")
        self.stdout.write("="*60)

        # Delete everything in reverse dependency order
        self.stdout.write("\n🗑️ Deleting old data...")
        
        try:
            data_count = Data.objects.count()
            Data.objects.all().delete()
            self.stdout.write(f"✅ Deleted {data_count} Data records")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Data: {e}"))

        try:
            attr_count = Atributes.objects.count()
            Atributes.objects.all().delete()
            self.stdout.write(f"✅ Deleted {attr_count} Atributes records")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Atribute: {e}"))

        try:
            sys_count = System.objects.count()
            System.objects.all().delete()
            self.stdout.write(f"✅ Deleted {sys_count} System records")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ System: {e}"))

        try:
            obj_count = Obj.objects.count()
            Obj.objects.all().delete()
            self.stdout.write(f"✅ Deleted {obj_count} Obj records")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Obj: {e}"))

        # Load quality demo data
        self.stdout.write("\n📊 Loading 10 quality objects...")
        self.stdout.write("-"*60)

        try:
            call_command('load_quality_demo')
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS("✅ SUCCESS! NEW DATA LOADED"))
            self.stdout.write("="*60)
            
            self.stdout.write(f"\n📊 Results:")
            self.stdout.write(f"   Objects: {Obj.objects.count()}")
            self.stdout.write(f"   Systems: {System.objects.count()}")
            self.stdout.write(f"   Sensors: {Atributes.objects.count()}")
            self.stdout.write(f"   Data points: {Data.objects.count()}")
            self.stdout.write(f"\n🌐 Check: https://www.promonitor.kz/dashboard/")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ ERROR: {e}"))
            raise
