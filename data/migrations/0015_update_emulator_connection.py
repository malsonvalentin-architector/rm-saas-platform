# Generated migration for updating Modbus connection
from django.db import migrations

def update_emulator_connection(apps, schema_editor):
    ModbusConnection = apps.get_model('data', 'ModbusConnection')
    try:
        conn = ModbusConnection.objects.get(name="Enhanced Emulator v2.0")
        conn.host = "promonitor-modbus-emulator-production.up.railway.app"
        conn.port = 8000
        conn.save()
        print(f"✅ Updated connection: {conn.host}:{conn.port}")
    except ModbusConnection.DoesNotExist:
        print("⚠️ Enhanced Emulator v2.0 not found")

class Migration(migrations.Migration):
    dependencies = [
        ('data', '0014_populate_enhanced_emulator_v2'),
    ]
    
    operations = [
        migrations.RunPython(update_emulator_connection),
    ]
