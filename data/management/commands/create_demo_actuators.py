"""
Management команда для создания демо данных Phase 4.4

Создаёт тестовые актуаторы и команды управления
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from data.models import Company, Obj, System, Actuator, ActuatorCommand, User_profile
import random


class Command(BaseCommand):
    help = 'Создаёт демо данные для Phase 4.4: Actuators & Control'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('📦 СОЗДАНИЕ ДЕМО ДАННЫХ ДЛЯ PHASE 4.4: ACTUATORS & CONTROL'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Получаем первую компанию и её объекты
        try:
            company = Company.objects.first()
            if not company:
                self.stdout.write(self.style.ERROR('❌ Компании не найдены'))
                return
            
            self.stdout.write(f"✅ Компания: {company.name}")
            
            # Получаем системы
            systems = System.objects.filter(obj__company=company)[:5]
            if not systems:
                self.stdout.write(self.style.ERROR('❌ Системы не найдены'))
                return
            
            self.stdout.write(f"✅ Найдено систем: {systems.count()}\n")
            
            # Получаем первого пользователя для команд
            user = User_profile.objects.filter(company=company).first()
            if not user:
                self.stdout.write(self.style.WARNING('⚠️ Пользователь не найден, команды будут без пользователя'))
            
            # Удаляем старые демо данные
            old_count = Actuator.objects.filter(sys__obj__company=company).count()
            if old_count > 0:
                self.stdout.write(f"🗑️ Удаление старых демо данных ({old_count} актуаторов)...")
                Actuator.objects.filter(sys__obj__company=company).delete()
            
            # Типы актуаторов для создания
            actuator_configs = [
                # Клапаны
                {
                    'name': 'Главный клапан подачи',
                    'actuator_type': 'valve',
                    'description': 'Основной клапан управления потоком холодной воды',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 50,
                    'uom': '%',
                    'register': 1001,
                },
                {
                    'name': 'Клапан обратки',
                    'actuator_type': 'valve',
                    'description': 'Клапан управления обратным потоком',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 40,
                    'uom': '%',
                    'register': 1002,
                },
                # Реле
                {
                    'name': 'Реле питания компрессора',
                    'actuator_type': 'relay',
                    'description': 'Управление питанием основного компрессора',
                    'min_value': 0,
                    'max_value': 1,
                    'default_value': 0,
                    'uom': '',
                    'register': 2001,
                },
                {
                    'name': 'Реле аварийной сигнализации',
                    'actuator_type': 'relay',
                    'description': 'Включение/выключение аварийной сирены',
                    'min_value': 0,
                    'max_value': 1,
                    'default_value': 0,
                    'uom': '',
                    'register': 2002,
                },
                # Насосы
                {
                    'name': 'Насос циркуляции',
                    'actuator_type': 'pump',
                    'description': 'Циркуляционный насос системы охлаждения',
                    'min_value': 0,
                    'max_value': 1,
                    'default_value': 1,
                    'uom': '',
                    'register': 3001,
                },
                # Вентиляторы
                {
                    'name': 'Вентилятор конденсатора',
                    'actuator_type': 'fan',
                    'description': 'Управление скоростью вентилятора',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 60,
                    'uom': '%',
                    'register': 4001,
                },
                {
                    'name': 'Вентилятор испарителя',
                    'actuator_type': 'fan',
                    'description': 'Регулировка скорости вентилятора испарителя',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 70,
                    'uom': '%',
                    'register': 4002,
                },
                # Нагреватели
                {
                    'name': 'ТЭН оттайки',
                    'actuator_type': 'heater',
                    'description': 'Нагреватель для оттайки испарителя',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 0,
                    'uom': '%',
                    'register': 5001,
                },
                # Моторы
                {
                    'name': 'Мотор заслонки',
                    'actuator_type': 'motor',
                    'description': 'Привод воздушной заслонки',
                    'min_value': 0,
                    'max_value': 100,
                    'default_value': 50,
                    'uom': '%',
                    'register': 6001,
                },
                # Выключатели
                {
                    'name': 'Выключатель освещения',
                    'actuator_type': 'switch',
                    'description': 'Управление освещением камеры',
                    'min_value': 0,
                    'max_value': 1,
                    'default_value': 0,
                    'uom': '',
                    'register': 7001,
                },
            ]
            
            created_actuators = []
            
            # Создаём актуаторы
            self.stdout.write("\n🎮 Создание актуаторов:\n")
            for i, config in enumerate(actuator_configs):
                system = systems[i % len(systems)]
                
                actuator = Actuator.objects.create(
                    sys=system,
                    name=config['name'],
                    description=config['description'],
                    actuator_type=config['actuator_type'],
                    modbus_carel=True,
                    register=config['register'],
                    register_type='HD',
                    min_value=config['min_value'],
                    max_value=config['max_value'],
                    default_value=config['default_value'],
                    current_value=config['default_value'],
                    uom=config['uom'],
                    is_active=True,
                    is_online=random.choice([True, True, True, False]),  # 75% онлайн
                )
                
                created_actuators.append(actuator)
                
                status = "🟢 ОНЛАЙН" if actuator.is_online else "🔴 ОФЛАЙН"
                self.stdout.write(
                    f"  ✅ {config['actuator_type'].upper():8} | {config['name']:30} | {system.name:20} | {status}"
                )
            
            self.stdout.write(f"\n✅ Создано актуаторов: {len(created_actuators)}")
            
            # Создаём команды управления (история)
            self.stdout.write("\n📜 Создание истории команд:\n")
            commands_count = 0
            
            for actuator in created_actuators:
                # Создаём 5-15 команд для каждого актуатора
                num_commands = random.randint(5, 15)
                
                for _ in range(num_commands):
                    # Случайное время в прошлом (от 1 часа до 30 дней назад)
                    hours_ago = random.randint(1, 30*24)
                    executed_at = timezone.now() - timezone.timedelta(hours=hours_ago)
                    
                    # Случайное значение в диапазоне
                    if actuator.is_binary():
                        value = random.choice([0, 1])
                    else:
                        value = random.uniform(actuator.min_value, actuator.max_value)
                    
                    # Статус (95% успех, 5% ошибка)
                    status = random.choices(
                        ['success', 'failed', 'timeout'],
                        weights=[95, 3, 2]
                    )[0]
                    
                    # Время отклика (50-300 мс)
                    response_time = random.randint(50, 300) if status == 'success' else None
                    
                    command = ActuatorCommand.objects.create(
                        actuator=actuator,
                        command_value=value,
                        user=user if user else None,
                        status=status,
                        response_time_ms=response_time,
                        executed_at=executed_at,
                        source_ip=f"192.168.1.{random.randint(1, 254)}",
                        notes=random.choice([
                            '',
                            'Плановая настройка',
                            'Корректировка параметров',
                            'Тестовый запуск',
                            'Ручная корректировка',
                        ])
                    )
                    
                    commands_count += 1
                
                # Обновляем время последней команды
                last_command = ActuatorCommand.objects.filter(actuator=actuator).order_by('-executed_at').first()
                if last_command:
                    actuator.last_command_at = last_command.executed_at
                    actuator.save()
            
            self.stdout.write(f"✅ Создано команд: {commands_count}")
            
            # Статистика
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("📊 СТАТИСТИКА:\n"))
            
            total_actuators = Actuator.objects.filter(sys__obj__company=company).count()
            online_actuators = Actuator.objects.filter(sys__obj__company=company, is_online=True).count()
            total_commands = ActuatorCommand.objects.filter(actuator__sys__obj__company=company).count()
            success_commands = ActuatorCommand.objects.filter(
                actuator__sys__obj__company=company, 
                status='success'
            ).count()
            
            self.stdout.write(f"  Всего актуаторов: {total_actuators}")
            self.stdout.write(f"  В сети: {online_actuators}")
            self.stdout.write(f"  Всего команд: {total_commands}")
            self.stdout.write(f"  Успешных команд: {success_commands}")
            if total_commands > 0:
                self.stdout.write(f"  Успешность: {success_commands/total_commands*100:.1f}%")
            
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("✅ ДЕМО ДАННЫЕ УСПЕШНО СОЗДАНЫ!"))
            self.stdout.write(self.style.SUCCESS("="*70 + "\n"))
            
            self.stdout.write("🌐 Откройте: https://www.promonitor.kz/data/actuators/")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ОШИБКА: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
