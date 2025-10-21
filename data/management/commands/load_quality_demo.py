#!/usr/bin/env python
"""
Management Command: load_quality_demo

SIMPLIFIED VERSION - Guaranteed to work
Loads 10 quality demo objects with minimal complexity
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.models import Company, Obj, System, Atributes, Data
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Load 10 quality demo objects (SIMPLIFIED)'

    def handle(self, *args, **options):
        self.stdout.write("="*60)
        self.stdout.write("🏭 ProMonitor Quality Demo Data (SIMPLIFIED)")
        self.stdout.write("="*60)
        
        # Get company
        try:
            company = Company.objects.get(name='ProMonitor Demo')
            self.stdout.write(f"✅ Company: {company.name}")
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Company 'ProMonitor Demo' not found!"))
            return
        
        # Simple objects data
        objects_data = [
            {'name': 'Головной офис ProMonitor', 'address': 'г. Алматы, пр. Аль-Фараби 77'},
            {'name': 'Склад Алматы-1', 'address': 'г. Алматы, ул. Складская 15'},
            {'name': 'Склад Алматы-2', 'address': 'г. Алматы, ул. Промышленная 8'},
            {'name': 'Супермаркет Магнум №1', 'address': 'г. Алматы, мкр. Самал-2'},
            {'name': 'Супермаркет Магнум №2', 'address': 'г. Алматы, пр. Сейфуллина 458'},
            {'name': 'Магазин Мега Алматы', 'address': 'г. Алматы, ТРЦ Мега'},
            {'name': 'Гостиница Rixos', 'address': 'г. Алматы, пр. Сейфуллина 506'},
            {'name': 'Медцентр Interteach', 'address': 'г. Алматы, ул. Жандосова 98'},
            {'name': 'Ресторан Line Brew', 'address': 'г. Алматы, ул. Розыбакиева 289'},
            {'name': 'БЦ Nurly Tau', 'address': 'г. Алматы, пр. Аль-Фараби 19'},
        ]
        
        self.stdout.write("\n📊 Creating objects...")
        total_objects = 0
        total_systems = 0
        total_sensors = 0
        
        for obj_data in objects_data:
            try:
                # Create object
                obj = Obj.objects.create(
                    obj=obj_data['name'],
                    address=obj_data['address'],
                    company=company
                )
                total_objects += 1
                self.stdout.write(f"  ✅ {obj.obj}")
                
                # Create 4 systems per object
                for i in range(1, 5):
                    system = System.objects.create(
                        name=f"SYS-{total_systems+1:03d}",
                        obj=obj,
                        ipaddr=f"192.168.1.{100 + total_systems}"
                    )
                    total_systems += 1
                    
                    # Create 5 sensors per system
                    for j in range(1, 6):
                        sensor = Atributes.objects.create(
                            atribute=f"Sensor-{total_sensors+1:03d}",
                            uom="°C",
                            system=system
                        )
                        total_sensors += 1
                        
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ⚠️ Error creating {obj_data['name']}: {e}"))
                continue
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ DEMO DATA LOADED!"))
        self.stdout.write("="*60)
        self.stdout.write(f"\n📊 Results:")
        self.stdout.write(f"   Objects: {total_objects}")
        self.stdout.write(f"   Systems: {total_systems}")
        self.stdout.write(f"   Sensors: {total_sensors}")
        self.stdout.write(f"\n🌐 Check: https://www.promonitor.kz/dashboard/")
