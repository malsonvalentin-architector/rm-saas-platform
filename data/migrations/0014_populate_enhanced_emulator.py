# Generated automatically for Phase 4.6 - Enhanced Emulator Integration
from django.db import migrations
from django.utils import timezone

def populate_enhanced_emulator(apps, schema_editor):
    """
    Populate Enhanced Emulator v2.0 connection and register mappings
    """
    pass  # RunSQL will handle this

def reverse_populate(apps, schema_editor):
    """
    Remove Enhanced Emulator integration data
    """
    pass  # RunSQL will handle this

class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_add_modbus_models'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Create connection and mappings (FIXED: NOW() replaced with CURRENT_TIMESTAMP)
            sql="""
            -- Insert ModbusConnection for Enhanced Emulator v2.0
            INSERT INTO data_modbusconnection (
                name, host, port, protocol, slave_id, timeout, poll_interval, 
                enabled, description, created_at, updated_at
            ) VALUES (
                'Enhanced Emulator v2.0',
                'localhost',
                5020,
                'TCP',
                1,
                10.0,
                60.0,
                true,
                'Enhanced Modbus Emulator with 800+ registers for HVAC monitoring',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING;

            -- Insert 12 Register Mappings (using RETURNING to get connection_id)
            WITH emulator_conn AS (
                SELECT id FROM data_modbusconnection WHERE name = 'Enhanced Emulator v2.0' LIMIT 1
            )
            INSERT INTO data_modbusregistermap (
                connection_id, sensor_name, register_type, address, 
                data_type, scale_factor, "offset", enabled, description, 
                created_at, updated_at
            )
            SELECT 
                emulator_conn.id,
                sensor_name,
                register_type,
                address,
                data_type,
                scale_factor,
                "offset",
                enabled,
                description,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            FROM emulator_conn, (VALUES
                -- Temperature Sensors (4 zones) - Float32 = 2 registers each, step by 2
                ('Zone 1 Temperature', 'holding', 1000, 'float32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 1 (18-25°C range)'),
                ('Zone 2 Temperature', 'holding', 1002, 'float32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 2 (18-25°C range)'),
                ('Zone 3 Temperature', 'holding', 1004, 'float32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 3 (18-25°C range)'),
                ('Zone 4 Temperature', 'holding', 1006, 'float32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 4 (18-25°C range)'),
                
                -- Humidity Sensors (3 zones) - Float32 = 2 registers each, step by 2
                ('Zone 1 Humidity', 'holding', 2000, 'float32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 1 (40-70% RH)'),
                ('Zone 2 Humidity', 'holding', 2002, 'float32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 2 (40-70% RH)'),
                ('Zone 3 Humidity', 'holding', 2004, 'float32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 3 (40-70% RH)'),
                
                -- Pressure Sensors (2 types) - Float32 = 2 registers each, step by 2
                ('High Pressure Sensor', 'holding', 3000, 'float32', 1.0, 0.0, true, 
                 'High pressure sensor (1-12 bar range)'),
                ('Low Pressure Sensor', 'holding', 3002, 'float32', 1.0, 0.0, true, 
                 'Low pressure sensor (1-12 bar range)'),
                
                -- Power Meters (3 phases) - Float32 = 2 registers each, step by 2
                ('Phase 1 Power', 'holding', 4000, 'float32', 1.0, 0.0, true, 
                 'Power consumption meter for Phase 1 (2-15 kW)'),
                ('Phase 2 Power', 'holding', 4002, 'float32', 1.0, 0.0, true, 
                 'Power consumption meter for Phase 2 (2-15 kW)'),
                ('Phase 3 Power', 'holding', 4004, 'float32', 1.0, 0.0, true, 
                 'Power consumption meter for Phase 3 (2-15 kW)')
            ) AS mappings(
                sensor_name, register_type, address, data_type, 
                scale_factor, "offset", enabled, description
            )
            ON CONFLICT DO NOTHING;
            """,
            
            # Reverse SQL - Remove all data
            reverse_sql="""
            -- Delete register mappings first (foreign key constraint)
            DELETE FROM data_modbusregistermap 
            WHERE connection_id IN (
                SELECT id FROM data_modbusconnection 
                WHERE name = 'Enhanced Emulator v2.0'
            );
            
            -- Delete connection
            DELETE FROM data_modbusconnection 
            WHERE name = 'Enhanced Emulator v2.0';
            """
        ),
    ]
