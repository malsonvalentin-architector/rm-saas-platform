"""
Команда для проверки всех ссылок между страницами в системе тревог
"""
from django.core.management.base import BaseCommand
from django.urls import reverse
from data.models import Company, AlertEvent, Obj, System


class Command(BaseCommand):
    help = 'Проверить все ссылки в системе тревог'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔗 ПРОВЕРКА ССЫЛОК В СИСТЕМЕ ТРЕВОГ'))
        self.stdout.write('=' * 70)
        
        try:
            company = Company.objects.first()
            if not company:
                self.stdout.write(self.style.ERROR('❌ Компания не найдена'))
                return
            
            # Получаем первое событие тревоги
            alert = AlertEvent.objects.filter(
                rule__attribute__sys__obj__company=company
            ).select_related(
                'rule__attribute__sys__obj'
            ).first()
            
            if not alert:
                self.stdout.write(self.style.WARNING('⚠️ События тревог не найдены'))
                self.stdout.write('   Выполните: python manage.py create_smart_alerts')
                return
            
            sensor = alert.rule.attribute
            system = sensor.sys
            obj = system.obj if system else None
            
            self.stdout.write(f'\n✅ Используем тестовую тревогу:')
            self.stdout.write(f'   ID: {alert.id}')
            self.stdout.write(f'   Правило: {alert.rule.name}')
            self.stdout.write(f'   Датчик: {sensor.name}')
            self.stdout.write(f'   Система: {system.name if system else "N/A"}')
            self.stdout.write(f'   Объект: {obj.obj if obj else "N/A"}')
            
            # Проверяем все URL
            self.stdout.write(f'\n🔗 ПРОВЕРКА URL:')
            
            urls_to_check = []
            
            # 1. Страница тревог
            alerts_url = reverse('data:alerts_list')
            urls_to_check.append(('Страница тревог', alerts_url, '🚨'))
            
            # 2. Детали тревоги
            alert_detail_url = reverse('data:alert_detail', kwargs={'alert_id': alert.id})
            urls_to_check.append(('Детали тревоги', alert_detail_url, '📋'))
            
            # 3. История датчика
            sensor_history_url = reverse('data:sensor_history', kwargs={'sensor_id': sensor.id})
            urls_to_check.append(('История датчика', sensor_history_url, '📊'))
            
            # 4. Объект (если есть)
            if obj:
                object_url = reverse('data:object_dashboard', kwargs={'object_id': obj.id})
                urls_to_check.append(('Дашборд объекта', object_url, '🏢'))
            
            # 5. Список систем объекта
            if obj:
                systems_url = reverse('data:system_list', kwargs={'object_id': obj.id})
                urls_to_check.append(('Системы объекта', systems_url, '⚙️'))
            
            # Выводим все URL
            for name, url, icon in urls_to_check:
                full_url = f'https://www.promonitor.kz{url}'
                self.stdout.write(f'   {icon} {name}:')
                self.stdout.write(f'      {full_url}')
            
            # Проверка обратных ссылок
            self.stdout.write(f'\n🔄 ОБРАТНЫЕ ССЫЛКИ:')
            
            # На странице объекта должны быть активные тревоги
            if obj:
                active_alerts_for_obj = AlertEvent.objects.filter(
                    rule__attribute__sys__obj=obj,
                    status='active'
                ).count()
                
                self.stdout.write(f'   📍 Объект "{obj.obj}":')
                self.stdout.write(f'      Активных тревог: {active_alerts_for_obj}')
                self.stdout.write(f'      Эти тревоги должны показываться на странице объекта')
            
            # На странице системы должны быть тревоги
            if system:
                active_alerts_for_system = AlertEvent.objects.filter(
                    rule__attribute__sys=system,
                    status='active'
                ).count()
                
                self.stdout.write(f'   ⚙️ Система "{system.name}":')
                self.stdout.write(f'      Активных тревог: {active_alerts_for_system}')
            
            # Проверка данных в таблице
            self.stdout.write(f'\n📊 ДАННЫЕ В ТАБЛИЦЕ ТРЕВОГ:')
            
            recent_alerts = AlertEvent.objects.filter(
                rule__attribute__sys__obj__company=company
            ).select_related(
                'rule__attribute__sys__obj'
            ).order_by('-triggered_at')[:5]
            
            self.stdout.write(f'\n   Последние 5 тревог:')
            for i, a in enumerate(recent_alerts, 1):
                sensor_name = a.rule.attribute.name
                sys_name = a.rule.attribute.sys.name if a.rule.attribute.sys else 'N/A'
                obj_name = a.rule.attribute.sys.obj.obj if a.rule.attribute.sys and a.rule.attribute.sys.obj else 'N/A'
                
                self.stdout.write(f'\n   {i}. {a.rule.name} ({a.get_status_display()})')
                self.stdout.write(f'      📊 Датчик: {sensor_name}')
                self.stdout.write(f'      ⚙️ Система: {sys_name}')
                self.stdout.write(f'      🏢 Объект: {obj_name}')
                self.stdout.write(f'      🔗 Ссылка на датчик: /sensors/{a.rule.attribute.id}/history/')
                self.stdout.write(f'      🔗 Ссылка на объект: /objects/{a.rule.attribute.sys.obj.id}/')
            
            # Итоговая проверка
            self.stdout.write(f'\n' + '=' * 70)
            self.stdout.write(self.style.SUCCESS('✅ ПРОВЕРКА ЗАВЕРШЕНА'))
            self.stdout.write('=' * 70)
            
            self.stdout.write(f'\n📝 ЧТО ПРОВЕРИТЬ ВРУЧНУЮ:')
            self.stdout.write(f'   1. Откройте: https://www.promonitor.kz/alerts/')
            self.stdout.write(f'   2. Кликните на название объекта в таблице')
            self.stdout.write(f'   3. Кликните на название системы в таблице')
            self.stdout.write(f'   4. Кликните на датчик (с иконкой 📊)')
            self.stdout.write(f'   5. Проверьте что каждая ссылка ведёт на правильную страницу')
            
            self.stdout.write(f'\n✨ ВСЕ ССЫЛКИ ДОЛЖНЫ РАБОТАТЬ!')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            import traceback
            traceback.print_exc()
