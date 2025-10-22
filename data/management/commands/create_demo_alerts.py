"""
Команда для создания демо-данных для системы тревог (Phase 4.3)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from data.models import (
    Company, AlertRule, AlertEvent, AlertComment, 
    Atributes, User_profile
)


class Command(BaseCommand):
    help = 'Создать демо-данные для системы тревог'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔔 Создание демо-данных для тревог...'))
        
        # Получаем компанию и датчики
        try:
            company = Company.objects.first()
            if not company:
                self.stdout.write(self.style.ERROR('❌ Компания не найдена. Создайте компанию сначала.'))
                return
            
            # Получаем датчики (атрибуты)
            sensors = list(Atributes.objects.all()[:20])
            if not sensors:
                self.stdout.write(self.style.ERROR('❌ Датчики не найдены. Создайте объекты с системами сначала.'))
                return
            
            # Получаем пользователей
            users = list(User_profile.objects.filter(company=company)[:5])
            if not users:
                self.stdout.write(self.style.ERROR('❌ Пользователи не найдены.'))
                return
            
            self.stdout.write(f'✅ Найдено: {len(sensors)} датчиков, {len(users)} пользователей')
            
            # 1. Создаём правила тревог
            self.stdout.write('\n📋 Создание правил тревог...')
            rules_created = 0
            
            rule_templates = [
                {
                    'name': 'Критическая температура',
                    'description': 'Температура превышает критический порог 35°C',
                    'condition': '>',
                    'threshold': 35.0,
                    'severity': 'critical',
                },
                {
                    'name': 'Высокая температура',
                    'description': 'Температура превышает 30°C',
                    'condition': '>',
                    'threshold': 30.0,
                    'severity': 'high',
                },
                {
                    'name': 'Низкая температура',
                    'description': 'Температура ниже 15°C',
                    'condition': '<',
                    'threshold': 15.0,
                    'severity': 'medium',
                },
                {
                    'name': 'Высокая влажность',
                    'description': 'Влажность превышает 80%',
                    'condition': '>',
                    'threshold': 80.0,
                    'severity': 'high',
                },
                {
                    'name': 'Низкая влажность',
                    'description': 'Влажность ниже 30%',
                    'condition': '<',
                    'threshold': 30.0,
                    'severity': 'medium',
                },
                {
                    'name': 'Высокое напряжение',
                    'description': 'Напряжение выше 240V',
                    'condition': '>',
                    'threshold': 240.0,
                    'severity': 'high',
                },
                {
                    'name': 'Низкое напряжение',
                    'description': 'Напряжение ниже 200V',
                    'condition': '<',
                    'threshold': 200.0,
                    'severity': 'critical',
                },
                {
                    'name': 'Превышение мощности',
                    'description': 'Мощность превышает 50 кВт',
                    'condition': '>',
                    'threshold': 50.0,
                    'severity': 'high',
                },
                {
                    'name': 'Высокий ток',
                    'description': 'Ток превышает 100A',
                    'condition': '>',
                    'threshold': 100.0,
                    'severity': 'medium',
                },
                {
                    'name': 'Обнаружен дым',
                    'description': 'Датчик дыма сработал',
                    'condition': '>',
                    'threshold': 0.5,
                    'severity': 'critical',
                },
            ]
            
            created_rules = []
            for i, template in enumerate(rule_templates):
                # Выбираем случайный датчик
                sensor = random.choice(sensors)
                
                rule, created = AlertRule.objects.get_or_create(
                    company=company,
                    attribute=sensor,
                    name=template['name'],
                    defaults={
                        'description': template['description'],
                        'condition': template['condition'],
                        'threshold': template['threshold'],
                        'severity': template['severity'],
                        'notify_email': True,
                        'notify_telegram': random.choice([True, False]),
                        'enabled': True,
                    }
                )
                
                if created:
                    created_rules.append(rule)
                    rules_created += 1
                    self.stdout.write(f'   ✅ {rule.name} ({rule.get_severity_display()})')
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Создано {rules_created} правил тревог'))
            
            # 2. Создаём события тревог (срабатывания)
            self.stdout.write('\n🚨 Создание событий тревог...')
            events_created = 0
            
            statuses = ['active', 'acknowledged', 'resolved', 'snoozed']
            now = timezone.now()
            
            for i in range(30):  # Создаём 30 событий
                rule = random.choice(created_rules if created_rules else list(AlertRule.objects.all()[:10]))
                
                # Генерируем значение которое нарушает порог
                if rule.condition == '>':
                    value = rule.threshold + random.uniform(1, 20)
                elif rule.condition == '<':
                    value = rule.threshold - random.uniform(1, 20)
                else:
                    value = rule.threshold + random.uniform(-10, 10)
                
                # Случайный статус
                status = random.choice(statuses)
                
                # Время срабатывания (от 1 часа до 7 дней назад)
                triggered_at = now - timedelta(
                    hours=random.randint(1, 168)
                )
                
                event = AlertEvent.objects.create(
                    rule=rule,
                    triggered_at=triggered_at,
                    value=value,
                    status=status,
                )
                
                # Заполняем дополнительные поля в зависимости от статуса
                if status in ['acknowledged', 'resolved']:
                    event.acknowledged_by = random.choice(users)
                    event.acknowledged_at = triggered_at + timedelta(minutes=random.randint(5, 30))
                    event.save()
                
                if status == 'resolved':
                    event.resolved_by = random.choice(users)
                    event.resolved_at = event.acknowledged_at + timedelta(minutes=random.randint(10, 120))
                    event.save()
                
                if status == 'snoozed':
                    event.snoozed_by = random.choice(users)
                    event.snooze_until = now + timedelta(hours=random.randint(1, 24))
                    event.save()
                
                events_created += 1
                
                # Добавляем комментарии к некоторым тревогам
                if random.random() > 0.6:  # 40% шанс
                    comments_count = random.randint(1, 3)
                    for _ in range(comments_count):
                        comment_texts = [
                            'Проверяю ситуацию',
                            'Выезжаю на объект',
                            'Проблема устранена',
                            'Требуется техническое обслуживание',
                            'Ложное срабатывание',
                            'Связался с техником',
                            'Перезагрузил систему',
                            'Настроил параметры',
                        ]
                        
                        AlertComment.objects.create(
                            event=event,
                            user=random.choice(users),
                            text=random.choice(comment_texts),
                        )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Создано {events_created} событий тревог'))
            
            # Статистика
            self.stdout.write('\n📊 Статистика:')
            self.stdout.write(f'   🔴 Критических: {AlertEvent.objects.filter(rule__severity="critical").count()}')
            self.stdout.write(f'   🟠 Высоких: {AlertEvent.objects.filter(rule__severity="high").count()}')
            self.stdout.write(f'   🟡 Средних: {AlertEvent.objects.filter(rule__severity="medium").count()}')
            self.stdout.write(f'   🔵 Низких: {AlertEvent.objects.filter(rule__severity="low").count()}')
            self.stdout.write(f'\n   ⚡ Активных: {AlertEvent.objects.filter(status="active").count()}')
            self.stdout.write(f'   ✅ Решённых: {AlertEvent.objects.filter(status="resolved").count()}')
            self.stdout.write(f'   💬 Комментариев: {AlertComment.objects.count()}')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Демо-данные успешно созданы!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            import traceback
            traceback.print_exc()
