"""
Management command для создания КАЧЕСТВЕННЫХ demo данных
Создаёт 10 объектов с полной системой мониторинга:
- Каждый объект имеет 3-5 систем
- Каждая система имеет 5-8 датчиков
- Все датчики имеют исторические данные за 24 часа
- Настроены alert rules для критичных параметров
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random

from data.models import Company, Obj, System, Atributes, Data, AlertRule

User = get_user_model()


class Command(BaseCommand):
    help = 'Load high-quality demo data: 10 objects with systems, sensors, data, alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin@promonitor.kz',
            help='User email to assign objects'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing objects first'
        )

    def handle(self, *args, **options):
        user_email = options['user']
        reset = options['reset']

        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('🏭 ProMonitor Quality Demo Data Generator'))
        self.stdout.write('=' * 80)
        self.stdout.write('')

        # Get user and company
        try:
            user = User.objects.get(email=user_email)
            company = user.company
            self.stdout.write(f'✅ User: {user.email}')
            self.stdout.write(f'✅ Company: {company.name}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User not found: {user_email}'))
            return

        # Reset if requested
        if reset:
            self.stdout.write('')
            self.stdout.write('⚠️  Resetting existing data...')
            Obj.objects.filter(company=company).delete()
            self.stdout.write(self.style.SUCCESS('✅ Old data deleted'))

        self.stdout.write('')
        self.stdout.write('📊 Creating demo data...')
        self.stdout.write('')

        # Define 10 realistic objects
        objects_data = [
            {
                'name': 'Дата-центр Алматы - Главный',
                'address': 'ул. Достык, 240, Алматы',
                'description': 'Основной дата-центр с серверными стойками и системой охлаждения',
                'systems': [
                    {'name': 'Серверная комната 1', 'sensors': ['Температура CPU', 'Влажность воздуха', 'Мощность серверов', 'Температура охлаждающей жидкости']},
                    {'name': 'Серверная комната 2', 'sensors': ['Температура CPU', 'Влажность воздуха', 'Мощность серверов', 'Давление в системе']},
                    {'name': 'Система кондиционирования', 'sensors': ['Температура на выходе', 'Мощность компрессора', 'Уровень фреона', 'Давление']},
                    {'name': 'ИБП (Источник бесперебойного питания)', 'sensors': ['Напряжение сети', 'Ток нагрузки', 'Заряд батареи %', 'Температура батарей']},
                    {'name': 'Система пожаротушения', 'sensors': ['Датчик дыма', 'Температура в помещении', 'Давление в системе', 'Состояние клапанов']},
                ]
            },
            {
                'name': 'Офисное здание на Абая',
                'address': 'пр. Абая, 143, Алматы',
                'description': 'Административное здание с офисными помещениями',
                'systems': [
                    {'name': 'HVAC 1-й этаж', 'sensors': ['Температура', 'Влажность', 'Расход воздуха', 'Давление']},
                    {'name': 'HVAC 2-й этаж', 'sensors': ['Температура', 'Влажность', 'Расход воздуха', 'Давление']},
                    {'name': 'Электрощитовая', 'sensors': ['Напряжение L1', 'Напряжение L2', 'Напряжение L3', 'Общая мощность', 'Ток L1', 'Ток L2', 'Ток L3']},
                    {'name': 'Система освещения', 'sensors': ['Мощность освещения', 'Освещённость', 'Состояние датчиков движения']},
                ]
            },
            {
                'name': 'Производственный цех №1',
                'address': 'ул. Промышленная, 15, Алматы',
                'description': 'Производственное помещение с технологическим оборудованием',
                'systems': [
                    {'name': 'Компрессорная станция', 'sensors': ['Давление нагнетания', 'Температура компрессора', 'Мощность двигателя', 'Вибрация', 'Уровень масла']},
                    {'name': 'Технологическая линия А', 'sensors': ['Скорость конвейера', 'Температура процесса', 'Давление гидросистемы', 'Энергопотребление']},
                    {'name': 'Технологическая линия Б', 'sensors': ['Скорость конвейера', 'Температура процесса', 'Давление гидросистемы', 'Энергопотребление']},
                    {'name': 'Вентиляция цеха', 'sensors': ['Расход воздуха', 'Температура приточного воздуха', 'Мощность вентиляторов', 'Фильтры - перепад давления']},
                ]
            },
            {
                'name': 'Торговый центр Mega',
                'address': 'ул. Розыбакиева, 247, Алматы',
                'description': 'Крупный торговый центр с системами климат-контроля',
                'systems': [
                    {'name': 'Чиллер 1', 'sensors': ['Температура подачи', 'Температура обратки', 'Мощность чиллера', 'Давление фреона', 'Расход воды']},
                    {'name': 'Чиллер 2', 'sensors': ['Температура подачи', 'Температура обратки', 'Мощность чиллера', 'Давление фреона', 'Расход воды']},
                    {'name': 'Вентиляция торгового зала', 'sensors': ['CO2 в зале', 'Температура', 'Влажность', 'Расход воздуха']},
                    {'name': 'Холодильные витрины', 'sensors': ['Температура витрины 1', 'Температура витрины 2', 'Температура витрины 3', 'Общая мощность']},
                ]
            },
            {
                'name': 'Складской комплекс на Жандосова',
                'address': 'ул. Жандосова, 98, Алматы',
                'description': 'Складские помещения с холодильными камерами',
                'systems': [
                    {'name': 'Холодильная камера №1', 'sensors': ['Температура воздуха', 'Влажность', 'Температура испарителя', 'Давление фреона']},
                    {'name': 'Холодильная камера №2', 'sensors': ['Температура воздуха', 'Влажность', 'Температура испарителя', 'Давление фреона']},
                    {'name': 'Погрузочная зона', 'sensors': ['Температура', 'Освещённость', 'Энергопотребление']},
                ]
            },
            {
                'name': 'Больничный комплекс',
                'address': 'ул. Байзакова, 280, Алматы',
                'description': 'Медицинское учреждение с критичными системами',
                'systems': [
                    {'name': 'Операционный блок', 'sensors': ['Температура', 'Влажность', 'Давление', 'Чистота воздуха', 'Содержание O2']},
                    {'name': 'Реанимация', 'sensors': ['Температура', 'Влажность', 'Давление', 'Содержание O2']},
                    {'name': 'Дизель-генератор', 'sensors': ['Напряжение', 'Частота', 'Мощность', 'Температура масла', 'Уровень топлива']},
                    {'name': 'Система вентиляции', 'sensors': ['Расход воздуха палаты', 'Расход воздуха коридоры', 'Температура', 'CO2']},
                ]
            },
            {
                'name': 'Гостиница Казжол',
                'address': 'пр. Достык, 52/2, Алматы',
                'description': 'Гостиничный комплекс с системами комфорта',
                'systems': [
                    {'name': 'Котельная', 'sensors': ['Температура теплоносителя', 'Давление в системе', 'Мощность котла', 'Расход газа']},
                    {'name': 'Кондиционирование номеров', 'sensors': ['Температура среднее', 'Влажность среднее', 'Мощность VRV систем']},
                    {'name': 'Бассейн', 'sensors': ['Температура воды', 'pH воды', 'Уровень хлора', 'Влажность воздуха']},
                ]
            },
            {
                'name': 'Бизнес-центр Нурлы Тау',
                'address': 'пр. Кабанбай батыра, 43, Нур-Султан',
                'description': 'Современный бизнес-центр класса А',
                'systems': [
                    {'name': 'Центральный кондиционер', 'sensors': ['Температура подачи', 'Температура обратки', 'Мощность', 'Расход воздуха', 'Фильтры - загрязнённость']},
                    {'name': 'Лифтовое оборудование', 'sensors': ['Энергопотребление', 'Вибрация', 'Счётчик циклов', 'Температура двигателя']},
                    {'name': 'Подземная парковка', 'sensors': ['CO в воздухе', 'Температура', 'Освещённость', 'Мощность вентиляции']},
                    {'name': 'Электроснабжение', 'sensors': ['Напряжение ввод 1', 'Напряжение ввод 2', 'Общая мощность', 'Коэффициент мощности']},
                ]
            },
            {
                'name': 'Аптечный склад',
                'address': 'ул. Сатпаева, 90/21, Алматы',
                'description': 'Склад медикаментов с контролируемыми условиями',
                'systems': [
                    {'name': 'Холодильная комерческая', 'sensors': ['Температура зона 1', 'Температура зона 2', 'Влажность', 'Мощность холодильника']},
                    {'name': 'Морозильная камера', 'sensors': ['Температура', 'Влажность', 'Давление фреона', 'Аварийная сигнализация']},
                    {'name': 'Комната хранения', 'sensors': ['Температура', 'Влажность', 'Освещённость']},
                ]
            },
            {
                'name': 'Ресторан Рахат',
                'address': 'ул. Фурманова, 273, Алматы',
                'description': 'Ресторанный комплекс с кухней и залом',
                'systems': [
                    {'name': 'Кухонная вытяжка', 'sensors': ['Расход воздуха', 'Температура', 'Жир на фильтрах %', 'Мощность вентилятора']},
                    {'name': 'Холодильные камеры кухни', 'sensors': ['Температура камера 1', 'Температура камера 2', 'Влажность', 'Общая мощность']},
                    {'name': 'Кондиционирование зала', 'sensors': ['Температура', 'Влажность', 'CO2', 'Мощность']},
                ]
            },
        ]

        total_objects = 0
        total_systems = 0
        total_sensors = 0
        total_data_points = 0
        total_alerts = 0

        for obj_data in objects_data:
            # Create object
            obj = Obj.objects.create(
                name=obj_data['name'],
                address=obj_data['address'],
                company=company
            )
            total_objects += 1
            self.stdout.write(f'  📍 {obj.name}')

            # Create systems and sensors
            for sys_data in obj_data['systems']:
                system = System.objects.create(
                    name=sys_data['name'],
                    obj=obj
                )
                total_systems += 1
                self.stdout.write(f'      🔧 {system.name}')

                # Create sensors
                for sensor_name in sys_data['sensors']:
                    # Determine sensor type and unit
                    if 'температур' in sensor_name.lower():
                        uom = '°C'
                        min_val, max_val = 18, 28
                        target = 22
                    elif 'влажн' in sensor_name.lower():
                        uom = '%'
                        min_val, max_val = 40, 70
                        target = 50
                    elif 'мощн' in sensor_name.lower():
                        uom = 'кВт'
                        min_val, max_val = 50, 200
                        target = 120
                    elif 'давлен' in sensor_name.lower():
                        uom = 'бар'
                        min_val, max_val = 1.5, 5.0
                        target = 3.0
                    elif 'напряжен' in sensor_name.lower():
                        uom = 'В'
                        min_val, max_val = 220, 230
                        target = 225
                    elif 'ток' in sensor_name.lower():
                        uom = 'А'
                        min_val, max_val = 10, 80
                        target = 45
                    elif 'co2' in sensor_name.lower():
                        uom = 'ppm'
                        min_val, max_val = 400, 1200
                        target = 800
                    elif 'расход' in sensor_name.lower():
                        uom = 'м³/ч'
                        min_val, max_val = 500, 3000
                        target = 1800
                    else:
                        uom = 'ед'
                        min_val, max_val = 0, 100
                        target = 50

                    sensor = Atributes.objects.create(
                        name=sensor_name,
                        sys=system,
                        uom=uom,
                        write=False
                    )
                    total_sensors += 1

                    # Generate 24 hours of data (every 5 minutes = 288 points)
                    now = timezone.now()
                    for i in range(288):
                        timestamp = now - timedelta(minutes=i * 5)
                        # Generate realistic value with some variation
                        base_value = target + random.uniform(-3, 3)
                        # Add daily cycle
                        hour_factor = (timestamp.hour - 12) / 12  # -1 to 1
                        cycle_value = base_value + hour_factor * (max_val - min_val) * 0.1
                        # Add random noise
                        final_value = cycle_value + random.uniform(-1, 1)
                        # Clamp to range
                        final_value = max(min_val, min(max_val, final_value))

                        Data.objects.create(
                            name=sensor,
                            date=timestamp,
                            value=round(final_value, 2)
                        )
                        total_data_points += 1

                    # Create alert rules for critical sensors
                    if 'температур' in sensor_name.lower() or 'мощн' in sensor_name.lower():
                        # High threshold alert
                        AlertRule.objects.create(
                            company=company,
                            attribute=sensor,
                            name=f'Высокая {sensor_name.lower()}',
                            condition='greater_than',
                            threshold=max_val - 2,
                            severity='warning',
                            enabled=True
                        )
                        # Critical threshold alert
                        AlertRule.objects.create(
                            company=company,
                            attribute=sensor,
                            name=f'Критическая {sensor_name.lower()}',
                            condition='greater_than',
                            threshold=max_val,
                            severity='critical',
                            enabled=True
                        )
                        total_alerts += 2

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ Demo data created successfully!'))
        self.stdout.write('=' * 80)
        self.stdout.write('')
        self.stdout.write(f'📊 Statistics:')
        self.stdout.write(f'   • Objects:     {total_objects}')
        self.stdout.write(f'   • Systems:     {total_systems}')
        self.stdout.write(f'   • Sensors:     {total_sensors}')
        self.stdout.write(f'   • Data points: {total_data_points}')
        self.stdout.write(f'   • Alert rules: {total_alerts}')
        self.stdout.write('')
        self.stdout.write(f'🌐 You can now access:')
        self.stdout.write(f'   • Objects list: /objects/')
        self.stdout.write(f'   • Each object dashboard with real-time data')
        self.stdout.write(f'   • Create new objects with form')
        self.stdout.write('')
