"""
Команда для проверки интеграции системы тревог с реальными данными
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from data.models import (
    Company, AlertRule, AlertEvent, Obj, System, 
    Atributes, Data
)


class Command(BaseCommand):
    help = 'Проверить интеграцию системы тревог'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 ПРОВЕРКА ИНТЕГРАЦИИ СИСТЕМЫ ТРЕВОГ'))
        self.stdout.write('=' * 70)
        
        try:
            # 1. Компания
            company = Company.objects.first()
            if not company:
                self.stdout.write(self.style.ERROR('❌ Компания не найдена'))
                return
            
            self.stdout.write(f'\n✅ Компания: {company.name} (ID={company.id})')
            
            # 2. Структура данных
            objects = Obj.objects.filter(company=company)
            systems = System.objects.filter(obj__company=company)
            sensors = Atributes.objects.filter(sys__obj__company=company)
            
            self.stdout.write(f'\n📊 СТРУКТУРА ДАННЫХ:')
            self.stdout.write(f'   • Объекты: {objects.count()}')
            self.stdout.write(f'   • Системы: {systems.count()}')
            self.stdout.write(f'   • Датчики: {sensors.count()}')
            
            # 3. Показания датчиков
            now = timezone.now()
            recent_data = Data.objects.filter(
                atribute__sys__obj__company=company,
                timestamp__gte=now - timedelta(hours=24)
            )
            
            self.stdout.write(f'\n📈 ДАННЫЕ ДАТЧИКОВ (24ч):')
            self.stdout.write(f'   • Показаний: {recent_data.count()}')
            
            # Топ-5 активных датчиков
            top_sensors = recent_data.values(
                'atribute__name',
                'atribute__sys__name',
                'atribute__sys__obj__obj'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            self.stdout.write(f'\n   🔥 Топ-5 активных датчиков:')
            for i, sensor_data in enumerate(top_sensors, 1):
                self.stdout.write(
                    f'      {i}. {sensor_data["atribute__name"]} '
                    f'@ {sensor_data["atribute__sys__name"]} '
                    f'({sensor_data["atribute__sys__obj__obj"]}): '
                    f'{sensor_data["count"]} показаний'
                )
            
            # 4. Правила тревог
            rules = AlertRule.objects.filter(company=company)
            active_rules = rules.filter(is_active=True)
            
            self.stdout.write(f'\n🔔 ПРАВИЛА ТРЕВОГ:')
            self.stdout.write(f'   • Всего правил: {rules.count()}')
            self.stdout.write(f'   • Активных: {active_rules.count()}')
            
            # По серьёзности
            by_severity = rules.values('severity').annotate(count=Count('id'))
            for item in by_severity:
                severity_icons = {
                    'low': '🔵',
                    'medium': '🟡',
                    'high': '🟠',
                    'critical': '🔴'
                }
                icon = severity_icons.get(item['severity'], '⚪')
                self.stdout.write(f'   {icon} {item["severity"]}: {item["count"]}')
            
            # Топ-5 правил
            if rules.exists():
                self.stdout.write(f'\n   📋 Топ-5 правил:')
                for i, rule in enumerate(rules[:5], 1):
                    sensor = rule.attribute
                    sys_name = sensor.sys.name if sensor.sys else 'N/A'
                    obj_name = sensor.sys.obj.obj if sensor.sys and sensor.sys.obj else 'N/A'
                    
                    self.stdout.write(
                        f'      {i}. {rule.name} '
                        f'({rule.get_severity_display()}) '
                        f'→ {sensor.name} @ {sys_name} ({obj_name})'
                    )
            
            # 5. События тревог
            events = AlertEvent.objects.filter(
                rule__company=company
            )
            
            self.stdout.write(f'\n🚨 СОБЫТИЯ ТРЕВОГ:')
            self.stdout.write(f'   • Всего событий: {events.count()}')
            
            # По статусам
            by_status = events.values('status').annotate(count=Count('id'))
            status_icons = {
                'active': '🔴',
                'acknowledged': '⚠️',
                'resolved': '✅',
                'snoozed': '⏰',
                'ignored': '🚫'
            }
            for item in by_status:
                icon = status_icons.get(item['status'], '⚪')
                self.stdout.write(f'   {icon} {item["status"]}: {item["count"]}')
            
            # Последние 5 событий
            if events.exists():
                self.stdout.write(f'\n   🔥 Последние 5 событий:')
                for i, event in enumerate(events.order_by('-triggered_at')[:5], 1):
                    rule = event.rule
                    sensor = rule.attribute
                    sys_name = sensor.sys.name if sensor.sys else 'N/A'
                    obj_name = sensor.sys.obj.obj if sensor.sys and sensor.sys.obj else 'N/A'
                    
                    time_str = event.triggered_at.strftime('%d.%m %H:%M')
                    status_icon = status_icons.get(event.status, '⚪')
                    
                    self.stdout.write(
                        f'      {i}. [{time_str}] {status_icon} {rule.name} '
                        f'({event.value} {sensor.uom}) '
                        f'@ {sys_name} ({obj_name})'
                    )
            
            # 6. Проверка связей
            self.stdout.write(f'\n🔗 ПРОВЕРКА СВЯЗЕЙ:')
            
            # Датчики с правилами
            sensors_with_rules = Atributes.objects.filter(
                sys__obj__company=company,
                alertrule__isnull=False
            ).distinct().count()
            
            # Правила с событиями
            rules_with_events = AlertRule.objects.filter(
                company=company,
                events__isnull=False
            ).distinct().count()
            
            # События с комментариями
            events_with_comments = AlertEvent.objects.filter(
                rule__company=company,
                comments__isnull=False
            ).distinct().count()
            
            self.stdout.write(f'   • Датчиков с правилами: {sensors_with_rules} / {sensors.count()}')
            self.stdout.write(f'   • Правил с событиями: {rules_with_events} / {rules.count()}')
            self.stdout.write(f'   • События с комментариями: {events_with_comments} / {events.count()}')
            
            # 7. Итоговая оценка
            self.stdout.write(f'\n' + '=' * 70)
            
            if events.count() == 0:
                self.stdout.write(self.style.WARNING('⚠️ НЕТ СОБЫТИЙ ТРЕВОГ'))
                self.stdout.write('   Выполните: python manage.py create_smart_alerts')
            elif events.filter(status='active').count() > 0:
                self.stdout.write(self.style.SUCCESS('✅ ИНТЕГРАЦИЯ РАБОТАЕТ!'))
                self.stdout.write(f'   🚨 Есть активные тревоги: {events.filter(status="active").count()}')
            else:
                self.stdout.write(self.style.SUCCESS('✅ ИНТЕГРАЦИЯ НАСТРОЕНА'))
                self.stdout.write('   ℹ️ Нет активных тревог (все решены)')
            
            self.stdout.write('=' * 70)
            self.stdout.write(f'\n🌐 Проверьте веб-интерфейс: https://www.promonitor.kz/alerts/')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            import traceback
            traceback.print_exc()
