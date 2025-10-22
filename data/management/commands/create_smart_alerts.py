"""
Умная команда для создания тревог на основе реальных данных (Phase 4.3)
Анализирует существующие показания датчиков и создаёт реалистичные тревоги
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Count
import random
from data.models import (
    Company, AlertRule, AlertEvent, AlertComment, 
    Atributes, User_profile, Data, Obj, System
)


class Command(BaseCommand):
    help = 'Создать умные тревоги на основе реальных данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--events',
            type=int,
            default=20,
            help='Количество событий тревог (по умолчанию: 20)'
        )

    def handle(self, *args, **options):
        events_count = options['events']
        
        self.stdout.write(self.style.SUCCESS('🚨 УМНАЯ ГЕНЕРАЦИЯ ТРЕВОГ'))
        self.stdout.write('=' * 60)
        
        try:
            # 1. Проверяем компанию
            company = Company.objects.first()
            if not company:
                self.stdout.write(self.style.ERROR('❌ Компания не найдена'))
                return
            
            self.stdout.write(f'\n✅ Компания: {company.name}')
            
            # 2. Получаем объекты, системы, датчики
            objects = Obj.objects.filter(company=company)
            systems = System.objects.filter(obj__company=company)
            sensors = Atributes.objects.filter(sys__obj__company=company)
            
            self.stdout.write(f'📊 Структура:')
            self.stdout.write(f'   • Объекты: {objects.count()}')
            self.stdout.write(f'   • Системы: {systems.count()}')
            self.stdout.write(f'   • Датчики: {sensors.count()}')
            
            if not sensors.exists():
                self.stdout.write(self.style.ERROR('❌ Датчики не найдены'))
                return
            
            # 3. Анализируем реальные данные
            self.stdout.write(f'\n🔍 АНАЛИЗ РЕАЛЬНЫХ ДАННЫХ...')
            
            sensors_with_data = []
            for sensor in sensors[:30]:  # Топ-30 датчиков
                recent_data = Data.objects.filter(
                    atribute=sensor,
                    timestamp__gte=timezone.now() - timedelta(days=7)
                )
                
                if recent_data.exists():
                    stats = recent_data.aggregate(
                        count=Count('id'),
                        avg=Avg('value'),
                        max_val=Max('value'),
                        min_val=Min('value')
                    )
                    
                    sensors_with_data.append({
                        'sensor': sensor,
                        'stats': stats,
                        'system': sensor.sys,
                        'object': sensor.sys.obj if sensor.sys else None
                    })
            
            self.stdout.write(f'✅ Датчиков с данными: {len(sensors_with_data)}')
            
            # Выводим топ-5 датчиков
            self.stdout.write(f'\n📈 Топ-5 датчиков с данными:')
            for i, item in enumerate(sensors_with_data[:5], 1):
                sensor = item['sensor']
                stats = item['stats']
                obj_name = item['object'].obj if item['object'] else 'N/A'
                sys_name = item['system'].name if item['system'] else 'N/A'
                
                self.stdout.write(
                    f'   {i}. {sensor.name} @ {sys_name} ({obj_name})\n'
                    f'      Данных: {stats["count"]}, '
                    f'Avg: {stats["avg"]:.1f}, '
                    f'Min: {stats["min_val"]:.1f}, '
                    f'Max: {stats["max_val"]:.1f} {sensor.uom}'
                )
            
            # 4. Получаем пользователей
            users = list(User_profile.objects.filter(company=company))
            if not users:
                self.stdout.write(self.style.WARNING('⚠️ Пользователи не найдены'))
                return
            
            self.stdout.write(f'\n👥 Пользователей: {len(users)}')
            
            # 5. Создаём правила тревог на основе реальных данных
            self.stdout.write(f'\n📋 СОЗДАНИЕ ПРАВИЛ ТРЕВОГ...')
            
            rules_created = 0
            created_rules = []
            
            for item in sensors_with_data[:10]:  # Создаём правила для топ-10 датчиков
                sensor = item['sensor']
                stats = item['stats']
                
                # Умные пороги на основе статистики
                avg_val = stats['avg']
                max_val = stats['max_val']
                min_val = stats['min_val']
                
                # Высокое значение (превышение на 20% от max)
                high_threshold = max_val * 1.2
                rule_high, created = AlertRule.objects.get_or_create(
                    company=company,
                    attribute=sensor,
                    name=f'Высокое {sensor.name}',
                    defaults={
                        'description': f'{sensor.name} превышает норму',
                        'condition': '>',
                        'threshold': high_threshold,
                        'severity': 'high',
                        'is_active': True,
                        'notification_channels': ['email', 'telegram']
                    }
                )
                
                if created:
                    created_rules.append(rule_high)
                    rules_created += 1
                    self.stdout.write(f'   ✅ {rule_high.name} (порог > {high_threshold:.1f})')
                
                # Низкое значение (ниже на 20% от min)
                low_threshold = min_val * 0.8
                rule_low, created = AlertRule.objects.get_or_create(
                    company=company,
                    attribute=sensor,
                    name=f'Низкое {sensor.name}',
                    defaults={
                        'description': f'{sensor.name} ниже нормы',
                        'condition': '<',
                        'threshold': low_threshold,
                        'severity': 'medium',
                        'is_active': True,
                        'notification_channels': ['email']
                    }
                )
                
                if created:
                    created_rules.append(rule_low)
                    rules_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Создано правил: {rules_created}'))
            
            # 6. Создаём события тревог на основе реальных данных
            self.stdout.write(f'\n🚨 СОЗДАНИЕ СОБЫТИЙ ТРЕВОГ...')
            
            events_created = 0
            statuses = ['active', 'acknowledged', 'resolved', 'snoozed']
            now = timezone.now()
            
            # Используем существующие правила
            all_rules = list(AlertRule.objects.filter(company=company))
            if not all_rules:
                all_rules = created_rules
            
            for i in range(events_count):
                rule = random.choice(all_rules)
                sensor = rule.attribute
                
                # Пытаемся найти реальное значение, которое нарушает порог
                recent_data = Data.objects.filter(
                    atribute=sensor,
                    timestamp__gte=now - timedelta(days=7)
                ).order_by('?')[:10]  # Случайные 10 записей
                
                triggered_value = None
                triggered_time = None
                
                for data_point in recent_data:
                    # Проверяем нарушает ли это значение порог
                    if rule.check_condition(data_point.value):
                        triggered_value = data_point.value
                        triggered_time = data_point.timestamp
                        break
                
                # Если не нашли реальное нарушение, генерируем
                if triggered_value is None:
                    if rule.condition == '>':
                        triggered_value = rule.threshold + random.uniform(1, 20)
                    elif rule.condition == '<':
                        triggered_value = rule.threshold - random.uniform(1, 20)
                    else:
                        triggered_value = rule.threshold + random.uniform(-10, 10)
                    
                    triggered_time = now - timedelta(hours=random.randint(1, 168))
                
                # Статус тревоги
                status = random.choice(statuses)
                
                # Создаём событие
                event = AlertEvent.objects.create(
                    rule=rule,
                    triggered_at=triggered_time,
                    value=triggered_value,
                    status=status,
                )
                
                # Заполняем дополнительные поля
                if status in ['acknowledged', 'resolved']:
                    event.acknowledged_by = random.choice(users)
                    event.acknowledged_at = triggered_time + timedelta(minutes=random.randint(5, 30))
                    event.save()
                
                if status == 'resolved':
                    event.resolved_by = random.choice(users)
                    event.resolved_at = event.acknowledged_at + timedelta(minutes=random.randint(10, 120))
                    event.save()
                    
                    # Добавляем комментарий к решённой тревоге
                    AlertComment.objects.create(
                        event=event,
                        user=event.resolved_by,
                        text=random.choice([
                            'Проблема устранена',
                            'Система восстановлена',
                            'Параметры приведены в норму',
                            'Выполнено техническое обслуживание',
                        ])
                    )
                
                if status == 'snoozed':
                    event.snoozed_by = random.choice(users)
                    event.snooze_until = now + timedelta(hours=random.randint(1, 24))
                    event.save()
                
                events_created += 1
                
                # Добавляем комментарии к некоторым тревогам
                if random.random() > 0.7:  # 30% шанс
                    comments_count = random.randint(1, 2)
                    for _ in range(comments_count):
                        comment_texts = [
                            'Проверяю ситуацию',
                            'Выезжаю на объект',
                            'Требуется техническое обслуживание',
                            'Связался с техником',
                            'Перезагрузил систему',
                            'Настроил параметры',
                        ]
                        
                        AlertComment.objects.create(
                            event=event,
                            user=random.choice(users),
                            text=random.choice(comment_texts),
                        )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Создано событий: {events_created}'))
            
            # 7. Статистика
            self.stdout.write(f'\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('📊 ФИНАЛЬНАЯ СТАТИСТИКА:'))
            self.stdout.write('=' * 60)
            
            self.stdout.write(f'\n🔔 Правила тревог:')
            self.stdout.write(f'   🔴 Критических: {AlertEvent.objects.filter(rule__severity="critical").count()}')
            self.stdout.write(f'   🟠 Высоких: {AlertEvent.objects.filter(rule__severity="high").count()}')
            self.stdout.write(f'   🟡 Средних: {AlertEvent.objects.filter(rule__severity="medium").count()}')
            self.stdout.write(f'   🔵 Низких: {AlertEvent.objects.filter(rule__severity="low").count()}')
            
            self.stdout.write(f'\n⚡ События тревог:')
            self.stdout.write(f'   🚨 Активных: {AlertEvent.objects.filter(status="active").count()}')
            self.stdout.write(f'   ⚠️ Подтверждённых: {AlertEvent.objects.filter(status="acknowledged").count()}')
            self.stdout.write(f'   ✅ Решённых: {AlertEvent.objects.filter(status="resolved").count()}')
            self.stdout.write(f'   ⏰ Отложенных: {AlertEvent.objects.filter(status="snoozed").count()}')
            self.stdout.write(f'   💬 Комментариев: {AlertComment.objects.count()}')
            
            self.stdout.write(f'\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('✅ УСПЕШНО! Умные тревоги созданы!'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'\n🌐 Проверьте: https://www.promonitor.kz/alerts/')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            import traceback
            traceback.print_exc()
