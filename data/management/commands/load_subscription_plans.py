"""
Management команда для загрузки тарифных планов и модулей
python manage.py load_subscription_plans
"""

from django.core.management.base import BaseCommand
from data.models import SubscriptionPlan, AddonModule
from decimal import Decimal


class Command(BaseCommand):
    help = 'Загрузить базовые тарифные планы и дополнительные модули'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Загрузка тарифных планов...\n')
        
        # ====================================================================
        # БАЗОВЫЕ ТАРИФНЫЕ ПЛАНЫ
        # ====================================================================
        
        plans_data = [
            {
                'name': 'BASIC',
                'slug': 'basic',
                'description': 'Идеально для малого бизнеса и стартапов',
                'price_monthly': Decimal('99.00'),
                'price_yearly': Decimal('950.40'),  # 20% скидка: 99*12*0.8
                'max_objects': 3,
                'max_systems': 10,
                'max_users': 5,
                'max_data_retention_days': 30,
                'has_api_access': False,
                'has_custom_reports': False,
                'has_white_label': False,
                'has_priority_support': False,
                'has_sla': False,
                'sort_order': 1,
                'is_featured': False,
            },
            {
                'name': 'PROFESSIONAL',
                'slug': 'professional',
                'description': 'Для растущих компаний с несколькими объектами',
                'price_monthly': Decimal('299.00'),
                'price_yearly': Decimal('2870.40'),  # 20% скидка
                'max_objects': 10,
                'max_systems': 50,
                'max_users': 20,
                'max_data_retention_days': 90,
                'has_api_access': True,
                'has_custom_reports': True,
                'has_white_label': False,
                'has_priority_support': True,
                'has_sla': False,
                'sort_order': 2,
                'is_featured': True,  # Рекомендуемый!
            },
            {
                'name': 'ENTERPRISE',
                'slug': 'enterprise',
                'description': 'Для крупных компаний с высокими требованиями',
                'price_monthly': Decimal('799.00'),
                'price_yearly': Decimal('7670.40'),  # 20% скидка
                'max_objects': 999,  # Практически безлимит
                'max_systems': 999,
                'max_users': 999,
                'max_data_retention_days': 365,
                'has_api_access': True,
                'has_custom_reports': True,
                'has_white_label': True,
                'has_priority_support': True,
                'has_sla': True,
                'sort_order': 3,
                'is_featured': False,
            },
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.update_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Создан план: {plan.name} (${plan.price_monthly}/мес)'))
            else:
                self.stdout.write(self.style.WARNING(f'  ♻️  Обновлён план: {plan.name}'))
        
        self.stdout.write('\n')
        
        # ====================================================================
        # ДОПОЛНИТЕЛЬНЫЕ МОДУЛИ
        # ====================================================================
        
        self.stdout.write('🎁 Загрузка дополнительных модулей...\n')
        
        modules_data = [
            # ------ AI CHAT ASSISTANT ------
            {
                'module_type': 'ai_assistant',
                'tier': 'starter',
                'name': 'AI Assistant Starter',
                'description': 'Базовый AI помощник для ответов на вопросы',
                'price_monthly': Decimal('43.00'),
                'ai_requests_limit': 500,
                'sort_order': 1,
                'is_coming_soon': True,  # Пока в разработке
            },
            {
                'module_type': 'ai_assistant',
                'tier': 'professional',
                'name': 'AI Assistant Professional',
                'description': 'Расширенный AI с углублённым анализом',
                'price_monthly': Decimal('98.00'),
                'ai_requests_limit': 2000,
                'sort_order': 2,
                'is_coming_soon': True,
            },
            {
                'module_type': 'ai_assistant',
                'tier': 'enterprise',
                'name': 'AI Assistant Enterprise',
                'description': 'Безлимитный AI с приоритетом обработки',
                'price_monthly': Decimal('217.00'),
                'ai_requests_limit': None,  # Безлимит
                'sort_order': 3,
                'is_coming_soon': True,
            },
            
            # ------ PREDICTIVE ANALYTICS ------
            {
                'module_type': 'predictive',
                'tier': 'basic',
                'name': 'Predictive Analytics Basic',
                'description': 'Базовое прогнозирование отказов оборудования',
                'price_monthly': Decimal('65.00'),
                'prediction_accuracy': 70,
                'prediction_days': 7,
                'sort_order': 4,
                'is_coming_soon': True,
            },
            {
                'module_type': 'predictive',
                'tier': 'pro',
                'name': 'Predictive Analytics Pro',
                'description': 'Точные прогнозы с машинным обучением',
                'price_monthly': Decimal('152.00'),
                'prediction_accuracy': 85,
                'prediction_days': 14,
                'sort_order': 5,
                'is_coming_soon': True,
            },
            {
                'module_type': 'predictive',
                'tier': 'enterprise',
                'name': 'Predictive Analytics Enterprise',
                'description': 'Максимальная точность и долгосрочные прогнозы',
                'price_monthly': Decimal('326.00'),
                'prediction_accuracy': 90,
                'prediction_days': 21,
                'sort_order': 6,
                'is_coming_soon': True,
            },
            
            # ------ AUTONOMOUS OPTIMIZATION ------
            {
                'module_type': 'optimization',
                'tier': 'basic',
                'name': 'Autonomous Optimization Basic',
                'description': 'Рекомендации по оптимизации энергопотребления',
                'price_monthly': Decimal('109.00'),
                'energy_saving_min': 10,
                'energy_saving_max': 15,
                'automation_level': 'Recommendations only',
                'sort_order': 7,
                'is_coming_soon': True,
            },
            {
                'module_type': 'optimization',
                'tier': 'pro',
                'name': 'Autonomous Optimization Pro',
                'description': 'Полуавтоматическая оптимизация с вашим одобрением',
                'price_monthly': Decimal('261.00'),
                'energy_saving_min': 15,
                'energy_saving_max': 20,
                'automation_level': 'Semi-autonomous',
                'sort_order': 8,
                'is_coming_soon': True,
            },
            {
                'module_type': 'optimization',
                'tier': 'enterprise',
                'name': 'Autonomous Optimization Enterprise',
                'description': 'Полностью автономная оптимизация 24/7',
                'price_monthly': Decimal('543.00'),
                'energy_saving_min': 20,
                'energy_saving_max': 30,
                'automation_level': 'Fully autonomous',
                'sort_order': 9,
                'is_coming_soon': True,
            },
        ]
        
        for module_data in modules_data:
            module, created = AddonModule.objects.update_or_create(
                module_type=module_data['module_type'],
                tier=module_data['tier'],
                defaults=module_data
            )
            
            status = '🔜 Coming Soon' if module.is_coming_soon else '✅ Active'
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ Создан модуль: {module.name} (${module.price_monthly}/мес) {status}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ♻️  Обновлён модуль: {module.name} {status}'
                    )
                )
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS('🎉 Все тарифные планы и модули загружены!'))
        self.stdout.write('\n')
        self.stdout.write('📊 Итого:')
        self.stdout.write(f'  • Базовых тарифов: {SubscriptionPlan.objects.count()}')
        self.stdout.write(f'  • Дополнительных модулей: {AddonModule.objects.count()}')
        self.stdout.write(f'    - AI Assistant: {AddonModule.objects.filter(module_type="ai_assistant").count()}')
        self.stdout.write(f'    - Predictive Analytics: {AddonModule.objects.filter(module_type="predictive").count()}')
        self.stdout.write(f'    - Autonomous Optimization: {AddonModule.objects.filter(module_type="optimization").count()}')
