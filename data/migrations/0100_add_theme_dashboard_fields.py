# Generated migration for ProMonitor V2 dashboard fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_rename_sensordata_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='theme',
            field=models.CharField(
                choices=[('light', 'Light'), ('dark', 'Dark')],
                default='dark',
                max_length=10,
                verbose_name='UI Theme'
            ),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='dashboard_version',
            field=models.CharField(
                choices=[('v1', 'Version 1'), ('v2', 'Version 2')],
                default='v2',
                max_length=10,
                verbose_name='Dashboard Version'
            ),
        ),
    ]