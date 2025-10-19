"""
DATA MIGRATION: Создание тарифных планов
Создает 3 базовых тарифа: Basic, Professional, Enterprise
"""

from django.db import migrations
from decimal import Decimal


def create_subscription_plans(apps, schema_editor):
    """Создает стандартные тарифные планы"""
    SubscriptionPlan = apps.get_model('data', 'SubscriptionPlan')
    
    plans = [
        {
            'name': 'Basic',
            'slug': 'basic',
            'description': 'Базовый тариф для малых предприятий',
            'price_monthly': Decimal('99.00'),
            'price_yearly': Decimal('990.00'),  # Скидка ~17%
            'max_objects': 5,
            'max_systems': 10,
            'max_users': 5,
            'max_data_retention_days': 30,
            'has_api_access': False,
            'has_telegram_notifications': False,
            'has_email_notifications': True,
            'has_custom_reports': False,
            'has_white_label': False,
            'has_priority_support': False,
            'is_active': True,
            'is_public': True,
            'sort_order': 1,
        },
        {
            'name': 'Professional',
            'slug': 'professional',
            'description': 'Профессиональный тариф для средних предприятий',
            'price_monthly': Decimal('299.00'),
            'price_yearly': Decimal('2990.00'),  # Скидка ~17%
            'max_objects': 20,
            'max_systems': 50,
            'max_users': 20,
            'max_data_retention_days': 90,
            'has_api_access': True,
            'has_telegram_notifications': True,
            'has_email_notifications': True,
            'has_custom_reports': True,
            'has_white_label': False,
            'has_priority_support': True,
            'is_active': True,
            'is_public': True,
            'sort_order': 2,
        },
        {
            'name': 'Enterprise',
            'slug': 'enterprise',
            'description': 'Корпоративный тариф для крупных предприятий',
            'price_monthly': Decimal('799.00'),
            'price_yearly': Decimal('7990.00'),  # Скидка ~17%
            'max_objects': 100,
            'max_systems': 500,
            'max_users': 100,
            'max_data_retention_days': 365,
            'has_api_access': True,
            'has_telegram_notifications': True,
            'has_email_notifications': True,
            'has_custom_reports': True,
            'has_white_label': True,
            'has_priority_support': True,
            'is_active': True,
            'is_public': True,
            'sort_order': 3,
        },
    ]
    
    for plan_data in plans:
        plan, created = SubscriptionPlan.objects.get_or_create(
            slug=plan_data['slug'],
            defaults=plan_data
        )
        
        if created:
            print(f"✓ Создан тарифный план: {plan.name} (${plan.price_monthly}/мес)")
        else:
            print(f"• Тариф {plan.name} уже существует")


def delete_subscription_plans(apps, schema_editor):
    """Удаляет созданные тарифные планы"""
    SubscriptionPlan = apps.get_model('data', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(slug__in=['basic', 'professional', 'enterprise']).delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('data', '0005_migrate_users_to_companies'),
    ]
    
    operations = [
        migrations.RunPython(
            create_subscription_plans,
            delete_subscription_plans
        ),
    ]
