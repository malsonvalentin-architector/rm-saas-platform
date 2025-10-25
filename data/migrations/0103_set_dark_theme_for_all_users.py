"""
Data migration to set dark theme for all existing users
"""
from django.db import migrations

def set_dark_theme(apps, schema_editor):
    """Set dark theme for all users"""
    User_profile = apps.get_model('data', 'User_profile')
    
    # Update all users to dark theme
    updated = User_profile.objects.all().update(theme='dark', dashboard_version='v2')
    
    print(f"✅ Updated {updated} users to dark theme and Dashboard V2")

def reverse_migration(apps, schema_editor):
    """Reverse operation - set light theme"""
    User_profile = apps.get_model('data', 'User_profile')
    User_profile.objects.all().update(theme='light', dashboard_version='v1')

class Migration(migrations.Migration):

    dependencies = [
        ('data', '0102_create_default_users'),
    ]

    operations = [
        migrations.RunPython(set_dark_theme, reverse_migration),
    ]
