# Generated migration to fix Modbus port after OSError 98 fix
from django.db import migrations

def update_modbus_port(apps, schema_editor):
    """Update Modbus connection to use port 5020 on private network"""
    ModbusConnection = apps.get_model('monitoring', 'ModbusConnection')
    
    # Update emulator connection to use port 5020
    connections = ModbusConnection.objects.filter(name__icontains='emulator')
    
    for conn in connections:
        # Update host to use Railway private network and port 5020
        conn.host = 'promonitor-modbus-emulator.railway.internal'
        conn.port = 5020
        conn.save()
        print(f"✅ Updated {conn.name}: {conn.host}:{conn.port}")

def reverse_update(apps, schema_editor):
    """Rollback to previous configuration"""
    ModbusConnection = apps.get_model('monitoring', 'ModbusConnection')
    
    connections = ModbusConnection.objects.filter(name__icontains='emulator')
    
    for conn in connections:
        conn.host = 'promonitor-modbus-emulator.railway.internal'
        conn.port = 502  # Default Modbus port
        conn.save()

class Migration(migrations.Migration):
    dependencies = [
        ('monitoring', '0018_use_private_networking'),
    ]

    operations = [
        migrations.RunPython(update_modbus_port, reverse_update),
    ]
