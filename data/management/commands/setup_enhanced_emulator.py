"""
Django Management Command: Setup Enhanced Emulator Integration
Автоматически создаёт Modbus Connection и 12 Register Mappings
"""
from django.core.management.base import BaseCommand
from data.models import ModbusConnection, ModbusRegisterMapping


class Command(BaseCommand):
    help = 'Setup Enhanced Modbus Emulator v2.0 integration'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🚀 Enhanced Emulator v2.0 Integration Setup"))
        self.stdout.write("=" * 70 + "\n")
        
        # === Step 1: Create Modbus Connection ===
        self.stdout.write(self.style.WARNING("📡 STEP 1: Creating Modbus Connection..."))
        self.stdout.write("-" * 70)
        
        conn, created = ModbusConnection.objects.get_or_create(
            name='Enhanced Emulator v2.0',
            defaults={
                'host': 'localhost',
                'port': 5020,
                'unit_id': 1,
                'connection_timeout': 5,
                'polling_interval': 5,
                'is_active': True,
                'description': 'Enhanced Modbus Emulator with 800+ registers (addresses 1000-4000)'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created new connection: {conn.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"ℹ️  Connection exists: {conn.name}"))
            conn.host = 'localhost'
            conn.port = 5020
            conn.is_active = True
            conn.save()
            self.stdout.write(self.style.SUCCESS("✅ Updated connection parameters"))
        
        self.stdout.write(f"   ID: {conn.id}")
        self.stdout.write(f"   Host: {conn.host}:{conn.port}")
        self.stdout.write(f"   Active: {conn.is_active}\n")
        
        # === Step 2: Create 12 Register Mappings ===
        self.stdout.write(self.style.WARNING("📊 STEP 2: Creating 12 Register Mappings..."))
        self.stdout.write("-" * 70)
        
        mappings = [
            # Temperature zones (1000-1003)
            (1000, 'Zone 1 Temperature', '°C', 'Temperature sensor for Zone 1 (18-25°C)'),
            (1001, 'Zone 2 Temperature', '°C', 'Temperature sensor for Zone 2 (18-25°C)'),
            (1002, 'Zone 3 Temperature', '°C', 'Temperature sensor for Zone 3 (18-25°C)'),
            (1003, 'Zone 4 Temperature', '°C', 'Temperature sensor for Zone 4 (18-25°C)'),
            
            # Humidity sensors (2000-2002)
            (2000, 'Humidity Sensor 1', '% RH', 'Humidity sensor 1 (40-70% RH)'),
            (2001, 'Humidity Sensor 2', '% RH', 'Humidity sensor 2 (40-70% RH)'),
            (2002, 'Humidity Sensor 3', '% RH', 'Humidity sensor 3 (40-70% RH)'),
            
            # Pressure sensors (3000-3001)
            (3000, 'High Pressure Sensor', 'bar', 'High pressure sensor (8-12 bar)'),
            (3001, 'Low Pressure Sensor', 'bar', 'Low pressure sensor (1-3 bar)'),
            
            # Power meters (4000-4002)
            (4000, 'Compressor 1 Power', 'kW', 'Compressor 1 power (5-15 kW)'),
            (4001, 'Compressor 2 Power', 'kW', 'Compressor 2 power (5-15 kW)'),
            (4002, 'Fans Total Power', 'kW', 'Fans total power (2-8 kW)'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for addr, name, unit, desc in mappings:
            mapping, created = ModbusRegisterMapping.objects.get_or_create(
                connection=conn,
                register_address=addr,
                defaults={
                    'register_type': 'holding_register',
                    'data_type': 'float32',
                    'sensor_name': name,
                    'unit': unit,
                    'scaling_factor': 1.0,
                    'offset': 0.0,
                    'is_active': True,
                    'description': desc,
                }
            )
            
            if created:
                self.stdout.write(f"  ✅ {name:30s} | Addr: {addr:5d} | {unit:6s}")
                created_count += 1
            else:
                mapping.sensor_name = name
                mapping.unit = unit
                mapping.is_active = True
                mapping.save()
                self.stdout.write(f"  ♻️  {name:30s} | Addr: {addr:5d} | {unit:6s}")
                updated_count += 1
        
        self.stdout.write(f"\n📈 Summary:")
        self.stdout.write(f"   Created: {created_count}")
        self.stdout.write(f"   Updated: {updated_count}")
        self.stdout.write(f"   Total:   {created_count + updated_count}\n")
        
        # === Step 3: Verification ===
        self.stdout.write(self.style.WARNING("✅ STEP 3: Verification"))
        self.stdout.write("-" * 70)
        
        active_conns = ModbusConnection.objects.filter(is_active=True).count()
        active_maps = ModbusRegisterMapping.objects.filter(
            connection=conn,
            is_active=True
        ).count()
        
        self.stdout.write(f"   Active Connections: {active_conns}")
        self.stdout.write(f"   Active Mappings:    {active_maps}")
        
        # Group by type
        temp = ModbusRegisterMapping.objects.filter(
            connection=conn, 
            register_address__gte=1000, 
            register_address__lt=2000,
            is_active=True
        ).count()
        
        hum = ModbusRegisterMapping.objects.filter(
            connection=conn,
            register_address__gte=2000,
            register_address__lt=3000,
            is_active=True
        ).count()
        
        press = ModbusRegisterMapping.objects.filter(
            connection=conn,
            register_address__gte=3000,
            register_address__lt=4000,
            is_active=True
        ).count()
        
        power = ModbusRegisterMapping.objects.filter(
            connection=conn,
            register_address__gte=4000,
            register_address__lt=5000,
            is_active=True
        ).count()
        
        self.stdout.write(f"\n   By type:")
        self.stdout.write(f"     🌡️  Temperature zones:  {temp}")
        self.stdout.write(f"     💧 Humidity sensors:   {hum}")
        self.stdout.write(f"     📊 Pressure sensors:   {press}")
        self.stdout.write(f"     ⚡ Power meters:       {power}")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("🎉 Integration Setup Complete!"))
        self.stdout.write("=" * 70 + "\n")
        
        self.stdout.write("Next steps:")
        self.stdout.write("1. Check Railway worker logs for polling activity")
        self.stdout.write("2. Check Railway beat logs for task scheduling")
        self.stdout.write("3. Verify data in Django Admin: /admin/data/modbusdata/")
        self.stdout.write("4. Expected: 12 new records every 5 seconds\n")
