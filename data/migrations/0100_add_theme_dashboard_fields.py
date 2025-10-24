# Generated migration for ProMonitor v2

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0099_auto_20250101_0000'),  # Update with actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='theme',
            field=models.CharField(
                max_length=10,
                choices=[('dark', 'Dark Theme'), ('light', 'Light Theme')],
                default='dark',
                verbose_name='Theme Preference'
            ),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='dashboard_version',
            field=models.CharField(
                max_length=10,
                choices=[('v1', 'Classic Dashboard'), ('v2', 'New Dashboard')],
                default='v2',  # v2 is main/default
                verbose_name='Dashboard Version'
            ),
        ),
    ]
