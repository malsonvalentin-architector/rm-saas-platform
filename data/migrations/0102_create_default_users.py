# Generated migration for creating default ProMonitor users

from django.db import migrations
from django.contrib.auth import get_user_model


def create_users(apps, schema_editor):
    """Create default users for ProMonitor"""
    User = get_user_model()
    Company = apps.get_model('data', 'Company')
    
    # Создаем или получаем demo компанию
    demo_company, _ = Company.objects.get_or_create(
        name='ProMonitor Demo',
        defaults={
            'description': 'Демонстрационная компания',
            'is_active': True
        }
    )
    
    # Список пользователей
    users_data = [
        {
            'email': 'superadmin@promonitor.kz',
            'password': 'Super123!',
            'role': 'superadmin',
            'first_name': 'Super',
            'last_name': 'Admin',
            'company': None,
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'email': 'admin@promonitor.kz',
            'password': 'Vika2025',
            'role': 'admin',
            'first_name': 'Vika',
            'last_name': 'Administrator',
            'company': demo_company,
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'email': 'manager@promonitor.kz',
            'password': 'Vika2025',
            'role': 'manager',
            'first_name': 'Vika',
            'last_name': 'Manager',
            'company': demo_company,
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'client@promonitor.kz',
            'password': 'Client123!',
            'role': 'client',
            'first_name': 'Client',
            'last_name': 'User',
            'company': demo_company,
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    for user_data in users_data:
        email = user_data['email']
        password = user_data.pop('password')
        
        # Создаем или обновляем пользователя
        user, created = User.objects.update_or_create(
            email=email,
            defaults=user_data
        )
        user.set_password(password)
        user.save()
        
        print(f"{'Created' if created else 'Updated'} user: {email}")


def remove_users(apps, schema_editor):
    """Remove created users on migration rollback"""
    User = get_user_model()
    
    emails = [
        'superadmin@promonitor.kz',
        'admin@promonitor.kz',
        'manager@promonitor.kz',
        'client@promonitor.kz',
    ]
    
    User.objects.filter(email__in=emails).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0101_add_ai_interaction_log'),
    ]

    operations = [
        migrations.RunPython(create_users, remove_users),
    ]
