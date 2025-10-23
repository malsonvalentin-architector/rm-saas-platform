# Generated migration for SensorData model
# Phase 4.6: Enhanced Emulator v2.0 Integration - Data Storage

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_populate_enhanced_emulator'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_value', models.FloatField(help_text='Значение напрямую из Modbus регистра', verbose_name='Сырое значение')),
                ('calculated_value', models.FloatField(help_text='После применения scale_factor и offset', verbose_name='Рассчитанное значение')),
                ('unit', models.CharField(blank=True, max_length=50, verbose_name='Единица измерения')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время получения')),
                ('quality', models.CharField(
                    choices=[('good', 'Хорошее'), ('uncertain', 'Неопределённое'), ('bad', 'Плохое')],
                    default='good',
                    max_length=20,
                    verbose_name='Качество данных'
                )),
                ('connection', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sensor_data',
                    to='data.modbusconnection',
                    verbose_name='Modbus соединение'
                )),
                ('register_map', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sensor_data',
                    to='data.modbusregistermap',
                    verbose_name='Регистр'
                )),
                ('sensor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='modbus_data',
                    to='data.sensor',
                    verbose_name='Датчик'
                )),
            ],
            options={
                'verbose_name': 'Данные датчика Modbus',
                'verbose_name_plural': 'Данные датчиков Modbus',
                'db_table': 'data_sensordata',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['-timestamp'], name='data_sensor_timesta_idx'),
                    models.Index(fields=['sensor', '-timestamp'], name='data_sensor_sensor_timesta_idx'),
                    models.Index(fields=['connection', '-timestamp'], name='data_sensor_connect_timesta_idx'),
                    models.Index(fields=['register_map', '-timestamp'], name='data_sensor_registe_timesta_idx'),
                ],
            },
        ),
    ]
