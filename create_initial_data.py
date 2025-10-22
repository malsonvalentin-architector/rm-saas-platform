"""
Script для создания начальных данных Modbus
Выполнить в Railway Shell: python create_initial_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmc.settings')
django.setup()

from data.models import ModbusConnection, ModbusRegisterMap, Sensor

print("🔧 Creating initial Modbus configuration...")

# Создаём подключение к эмулятору
emulator, created = ModbusConnection.objects.get_or_create(
    name="CAREL pCO Emulator",
    defaults={
        'host': 'localhost',
        'port': 5020,
        'protocol': 'tcp',
        'slave_id': 1,
        'timeout': 3,
        'poll_interval': 10,
        'enabled': True,
        'description': 'Modbus emulator with production data from CAREL pCO (192.168.11.101)'
    }
)

if created:
    print(f"✅ Created new connection: {emulator}")
else:
    print(f"ℹ️  Connection already exists: {emulator}")

# Создаём примеры register mappings для первых 5 датчиков
sensors = Sensor.objects.all()[:5]

for idx, sensor in enumerate(sensors):
    reg_map, created = ModbusRegisterMap.objects.get_or_create(
        connection=emulator,
        register_type='holding',
        address=idx,
        defaults={
            'sensor': sensor,
            'data_type': 'int16',
            'scale_factor': 0.1,
            'offset': 0.0,
            'enabled': True,
            'description': f'Auto-mapped: Holding Register {idx} -> {sensor.name}'
        }
    )
    
    if created:
        print(f"  ✅ Mapped: HR[{idx}] -> {sensor.name}")
    else:
        print(f"  ℹ️  Mapping already exists: HR[{idx}] -> {sensor.name}")

print("\n🎉 Initial configuration complete!")
print(f"   Connection: {emulator.name}")
print(f"   Registers mapped: {emulator.register_maps.count()}")
print(f"   Enabled: {emulator.enabled}")
print(f"\n📊 Next: Check /admin/data/modbusconnection/")
