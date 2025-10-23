# Generated automatically for Phase 4.6 - Enhanced Emulator Integration
from django.db import migrations

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
            # Forward SQL - Create connection and mappings
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
                5.0,
                true,
                'Enhanced Modbus Emulator with 800+ registers for HVAC monitoring',
                NOW(),
                NOW()
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
                NOW(),
                NOW()
            FROM emulator_conn, (VALUES
                -- Temperature Sensors (4 zones)
                ('Zone 1 Temperature', 'HOLDING', 1000, 'FLOAT32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 1 (18-25°C range)'),
                ('Zone 2 Temperature', 'HOLDING', 1001, 'FLOAT32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 2 (18-25°C range)'),
                ('Zone 3 Temperature', 'HOLDING', 1002, 'FLOAT32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 3 (18-25°C range)'),
                ('Zone 4 Temperature', 'HOLDING', 1003, 'FLOAT32', 1.0, 0.0, true, 
                 'Temperature sensor for Zone 4 (18-25°C range)'),
                
                -- Humidity Sensors (3 zones)
                ('Zone 1 Humidity', 'INPUT', 2000, 'FLOAT32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 1 (40-70% RH)'),
                ('Zone 2 Humidity', 'INPUT', 2001, 'FLOAT32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 2 (40-70% RH)'),
                ('Zone 3 Humidity', 'INPUT', 2002, 'FLOAT32', 1.0, 0.0, true, 
                 'Relative humidity sensor for Zone 3 (40-70% RH)'),
                
                -- Pressure Sensors (2 types)
                ('High Pressure Sensor', 'INPUT', 3000, 'FLOAT32', 1.0, 0.0, true, 
                 'High pressure sensor (1-12 bar range)'),
                ('Low Pressure Sensor', 'INPUT', 3001, 'FLOAT32', 1.0, 0.0, true, 
                 'Low pressure sensor (1-12 bar range)'),
                
                -- Power Meters (3 phases)
                ('Phase 1 Power', 'HOLDING', 4000, 'FLOAT32', 1.0, 0.0, true, 
                 'Power consumption meter for Phase 1 (2-15 kW)'),
                ('Phase 2 Power', 'HOLDING', 4001, 'FLOAT32', 1.0, 0.0, true, 
                 'Power consumption meter for Phase 2 (2-15 kW)'),
                ('Phase 3 Power', 'HOLDING', 4002, 'FLOAT32', 1.0, 0.0, true, 
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
