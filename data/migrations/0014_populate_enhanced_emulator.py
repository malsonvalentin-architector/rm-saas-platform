# Generated automatically for Phase 4.6 - Enhanced Emulator Integration
from django.db import migrations
from django.utils import timezone

def populate_enhanced_emulator(apps, schema_editor):
    """
    Populate Enhanced Emulator v2.0 connection and register mappings using ORM
    """
    ModbusConnection = apps.get_model('data', 'ModbusConnection')
    ModbusRegisterMap = apps.get_model('data', 'ModbusRegisterMap')
    
    # Create or get the connection
    connection, created = ModbusConnection.objects.get_or_create(
        name='Enhanced Emulator v2.0',
        defaults={
            'host': 'localhost',
            'port': 5020,
            'protocol': 'TCP',
            'slave_id': 1,
            'timeout': 10.0,
            'poll_interval': 60.0,
            'enabled': True,
            'description': 'Enhanced Modbus Emulator with 800+ registers for HVAC monitoring',
        }
    )
    
    # Define register mappings
    mappings = [
        # Temperature Sensors (4 zones) - Float32 = 2 registers each, step by 2
        {
            'sensor_name': 'Zone 1 Temperature',
            'register_type': 'holding',
            'address': 1000,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Temperature sensor for Zone 1 (18-25°C range)',
        },
        {
            'sensor_name': 'Zone 2 Temperature',
            'register_type': 'holding',
            'address': 1002,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Temperature sensor for Zone 2 (18-25°C range)',
        },
        {
            'sensor_name': 'Zone 3 Temperature',
            'register_type': 'holding',
            'address': 1004,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Temperature sensor for Zone 3 (18-25°C range)',
        },
        {
            'sensor_name': 'Zone 4 Temperature',
            'register_type': 'holding',
            'address': 1006,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Temperature sensor for Zone 4 (18-25°C range)',
        },
        # Humidity Sensors (3 zones) - Float32 = 2 registers each, step by 2
        {
            'sensor_name': 'Zone 1 Humidity',
            'register_type': 'holding',
            'address': 2000,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Relative humidity sensor for Zone 1 (40-70% RH)',
        },
        {
            'sensor_name': 'Zone 2 Humidity',
            'register_type': 'holding',
            'address': 2002,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Relative humidity sensor for Zone 2 (40-70% RH)',
        },
        {
            'sensor_name': 'Zone 3 Humidity',
            'register_type': 'holding',
            'address': 2004,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Relative humidity sensor for Zone 3 (40-70% RH)',
        },
        # Pressure Sensors (2 types) - Float32 = 2 registers each, step by 2
        {
            'sensor_name': 'High Pressure Sensor',
            'register_type': 'holding',
            'address': 3000,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'High pressure sensor (1-12 bar range)',
        },
        {
            'sensor_name': 'Low Pressure Sensor',
            'register_type': 'holding',
            'address': 3002,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Low pressure sensor (1-12 bar range)',
        },
        # Power Meters (3 phases) - Float32 = 2 registers each, step by 2
        {
            'sensor_name': 'Phase 1 Power',
            'register_type': 'holding',
            'address': 4000,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Power consumption meter for Phase 1 (2-15 kW)',
        },
        {
            'sensor_name': 'Phase 2 Power',
            'register_type': 'holding',
            'address': 4002,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Power consumption meter for Phase 2 (2-15 kW)',
        },
        {
            'sensor_name': 'Phase 3 Power',
            'register_type': 'holding',
            'address': 4004,
            'data_type': 'float32',
            'scale_factor': 1.0,
            'offset': 0.0,
            'enabled': True,
            'description': 'Power consumption meter for Phase 3 (2-15 kW)',
        },
    ]
    
    # Create register mappings
    for mapping_data in mappings:
        ModbusRegisterMap.objects.get_or_create(
            connection=connection,
            sensor_name=mapping_data['sensor_name'],
            defaults=mapping_data
        )

def reverse_populate(apps, schema_editor):
    """
    Remove Enhanced Emulator integration data
    """
    ModbusConnection = apps.get_model('data', 'ModbusConnection')
    ModbusRegisterMap = apps.get_model('data', 'ModbusRegisterMap')
    
    # Delete all related register maps first
    connection = ModbusConnection.objects.filter(name='Enhanced Emulator v2.0').first()
    if connection:
        ModbusRegisterMap.objects.filter(connection=connection).delete()
        connection.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_add_modbus_models'),
    ]

    operations = [
        migrations.RunPython(
            populate_enhanced_emulator,
            reverse_populate,
        ),
    ]
