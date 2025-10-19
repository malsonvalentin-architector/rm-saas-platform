"""
DATA MIGRATION: Перенос данных от пользователей к компаниям
Создает компании для существующих пользователей и переносит их объекты
"""

from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def create_companies_from_users(apps, schema_editor):
    """
    Создает компанию для каждого существующего пользователя
    и переносит его объекты в эту компанию
    """
    User_profile = apps.get_model('data', 'User_profile')
    Company = apps.get_model('data', 'Company')
    Obj = apps.get_model('data', 'Obj')
    
    # Для каждого пользователя создаем компанию
    for user in User_profile.objects.all():
        # Проверяем, нет ли уже компании для этого пользователя
        if user.company_id:
            continue
            
        # Создаем компанию
        company = Company.objects.create(
            name=f"Компания {user.email}",
            contact_person=f"{user.first_name} {user.last_name}".strip() or user.email,
            contact_email=user.email,
            contact_phone=user.phone_number or '',
            subscription_status='trial',
            trial_ends_at=timezone.now() + timedelta(days=30),  # 30 дней пробного периода
            is_active=True,
            notes=f"Автоматически создана при миграции для пользователя {user.email}"
        )
        
        # Привязываем пользователя к компании
        user.company = company
        # Делаем первого пользователя админом компании
        user.role = 'company_admin'
        user.save()
        
        # Переносим все объекты пользователя в компанию
        Obj.objects.filter(user=user).update(company=company)
        
        print(f"✓ Создана компания '{company.name}' для пользователя {user.email}")


def reverse_migration(apps, schema_editor):
    """
    Откат миграции - возвращаем объекты обратно пользователям
    """
    User_profile = apps.get_model('data', 'User_profile')
    Company = apps.get_model('data', 'Company')
    Obj = apps.get_model('data', 'Obj')
    
    # Для каждого объекта возвращаем привязку к пользователю
    for obj in Obj.objects.all():
        if obj.company_id:
            # Находим пользователя-админа этой компании
            user = User_profile.objects.filter(
                company_id=obj.company_id,
                role='company_admin'
            ).first()
            
            if user:
                obj.user = user
                obj.company = None
                obj.save()
    
    # Удаляем автоматически созданные компании
    Company.objects.all().delete()
    
    # Очищаем привязки пользователей к компаниям
    User_profile.objects.all().update(company=None, role='operator')


class Migration(migrations.Migration):
    
    dependencies = [
        ('data', '0004_add_multi_tenancy'),
    ]
    
    operations = [
        migrations.RunPython(
            create_companies_from_users,
            reverse_migration
        ),
    ]
