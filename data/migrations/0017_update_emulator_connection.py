# Generated migration for updating Modbus connection to Railway
from django.db import migrations

def update_emulator_connection(apps, schema_editor):
    ModbusConnection = apps.get_model('data', 'ModbusConnection')
    try:
        conn = ModbusConnection.objects.get(name="Enhanced Emulator v2.0")
        old_host = conn.host
        old_port = conn.port
        conn.host = "promonitor-modbus-emulator-production.up.railway.app"
        conn.port = 8000
        conn.save()
        print(f"✅ Updated connection from {old_host}:{old_port} to {conn.host}:{conn.port}")
    except ModbusConnection.DoesNotExist:
        print("⚠️ Enhanced Emulator v2.0 not found in database")

class Migration(migrations.Migration):
    dependencies = [
        ('data', '0016_rename_sensordata_indexes'),
    ]
    
    operations = [
        migrations.RunPython(update_emulator_connection),
    ]
