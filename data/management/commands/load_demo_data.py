"""
Management команда для загрузки демо-данных ProMonitor
Использование: python manage.py load_demo_data --user admin@promonitor.kz
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from data.models import Object, System, Attribute, Data, AlertRule

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка демо-данных для ProMonitor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin@promonitor.kz',
            help='Email пользователя для которого создавать данные'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед загрузкой'
        )

    def handle(self, *args, **options):
        user_email = options['user']
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Пользователь {user_email} не найден!'))
            return
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('Очистка существующих данных...'))
            Object.objects.filter(user=user).delete()
            self.stdout.write(self.style.SUCCESS('✓ Данные очищены'))
        
        self.stdout.write(self.style.SUCCESS(f'Загрузка демо-данных для {user_email}...'))
        
        # Создаём объекты
        objects_data = [
            {
                'name': 'Дата-центр Almaty DC1',
                'address': 'г. Алматы, ул. Абая 150/230',
                'description': 'Основной дата-центр с серверным оборудованием',
            },
            {
                'name': 'Офисный центр "Нурлы Тау"',
                'address': 'г. Астана, пр. Кабанбай батыра 47',
                'description': 'Административное здание с системами безопасности',
            },
            {
                'name': 'Производственный комплекс',
                'address': 'г. Караганда, промзона "Восток"',
                'description': 'Производственное здание с энергоёмким оборудованием',
            },
        ]
        
        created_objects = []
        for obj_data in objects_data:
            obj = Object.objects.create(
                user=user,
                name=obj_data['name'],
                address=obj_data['address'],
                description=obj_data['description']
            )
            created_objects.append(obj)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан объект: {obj.name}'))
        
        # Создаём системы и датчики для каждого объекта
        systems_config = [
            {
                'name': 'Система климат-контроля',
                'attributes': [
                    {'name': 'Температура воздуха', 'unit': '°C', 'min_val': 18, 'max_val': 28, 'room': 'Серверная', 'x': 25, 'y': 30},
                    {'name': 'Влажность воздуха', 'unit': '%', 'min_val': 40, 'max_val': 70, 'room': 'Серверная', 'x': 35, 'y': 40},
                    {'name': 'Температура офис', 'unit': '°C', 'min_val': 20, 'max_val': 26, 'room': 'Офис', 'x': 62, 'y': 35},
                ]
            },
            {
                'name': 'Система энергоснабжения',
                'attributes': [
                    {'name': 'Потребляемая мощность', 'unit': 'кВт', 'min_val': 50, 'max_val': 250, 'room': 'Серверная', 'x': 20, 'y': 60},
                    {'name': 'Напряжение питания', 'unit': 'В', 'min_val': 215, 'max_val': 235, 'room': 'Серверная', 'x': 30, 'y': 70},
                    {'name': 'Коэффициент мощности', 'unit': '', 'min_val': 0.85, 'max_val': 0.98, 'room': 'Серверная', 'x': 25, 'y': 80},
                ]
            },
            {
                'name': 'Система безопасности',
                'attributes': [
                    {'name': 'Датчик движения холл', 'unit': '', 'min_val': 0, 'max_val': 1, 'room': 'Коридор', 'x': 50, 'y': 75},
                    {'name': 'Датчик открытия двери', 'unit': '', 'min_val': 0, 'max_val': 1, 'room': 'Коридор', 'x': 40, 'y': 85},
                ]
            },
            {
                'name': 'Система вентиляции',
                'attributes': [
                    {'name': 'Скорость вентилятора 1', 'unit': 'об/мин', 'min_val': 800, 'max_val': 1500, 'room': 'Серверная', 'x': 15, 'y': 25},
                    {'name': 'Давление воздуха', 'unit': 'Па', 'min_val': 95, 'max_val': 105, 'room': 'Серверная', 'x': 20, 'y': 35},
                ]
            },
            {
                'name': 'Складская система',
                'attributes': [
                    {'name': 'Температура склада', 'unit': '°C', 'min_val': 15, 'max_val': 22, 'room': 'Склад', 'x': 87, 'y': 30},
                    {'name': 'Влажность склада', 'unit': '%', 'min_val': 35, 'max_val': 65, 'room': 'Склад', 'x': 90, 'y': 45},
                ]
            }
        ]
        
        total_sensors = 0
        
        for obj in created_objects:
            obj_systems = random.sample(systems_config, k=random.randint(3, 5))
            
            for sys_config in obj_systems:
                system = System.objects.create(
                    object=obj,
                    name=sys_config['name'],
                    description=f'{sys_config["name"]} для {obj.name}'
                )
                
                self.stdout.write(f'    ✓ Создана система: {system.name}')
                
                # Создаём датчики (атрибуты)
                for attr_config in sys_config['attributes']:
                    attribute = Attribute.objects.create(
                        system=system,
                        name=attr_config['name'],
                        unit=attr_config.get('unit', ''),
                        room=attr_config.get('room', 'Общая зона'),
                        x_position=attr_config.get('x', random.randint(20, 80)),
                        y_position=attr_config.get('y', random.randint(20, 80))
                    )
                    
                    total_sensors += 1
                    
                    # Генерируем исторические данные за последние 24 часа
                    now = timezone.now()
                    base_value = (attr_config['min_val'] + attr_config['max_val']) / 2
                    
                    for i in range(0, 24 * 12):  # Каждые 5 минут за 24 часа
                        timestamp = now - timedelta(minutes=5 * (24 * 12 - i))
                        
                        # Добавляем небольшой случайный шум
                        variation = (attr_config['max_val'] - attr_config['min_val']) * 0.1
                        value = base_value + random.uniform(-variation, variation)
                        
                        # Ограничиваем значение в диапазоне
                        value = max(attr_config['min_val'], min(attr_config['max_val'], value))
                        
                        Data.objects.create(
                            attribute=attribute,
                            value=round(value, 2),
                            timestamp=timestamp
                        )
                
                # Создаём несколько правил тревог для критичных датчиков
                critical_attrs = [attr for attr in system.attribute_set.all() 
                                if 'температур' in attr.name.lower() or 'мощн' in attr.name.lower()]
                
                for attr in critical_attrs[:2]:  # Только для первых двух критичных
                    if random.random() > 0.5:  # 50% вероятность создания алерта
                        AlertRule.objects.create(
                            system=system,
                            attribute=attr,
                            name=f'Превышение {attr.name}',
                            condition='greater_than',
                            threshold=attr.data_set.all().aggregate(
                                max_val=timezone.models.Max('value')
                            )['max_val'] * 0.9,  # 90% от максимального значения
                            is_active=random.random() > 0.7,  # 30% активных алертов
                            severity='warning' if random.random() > 0.5 else 'critical'
                        )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Демо-данные успешно загружены!'))
        self.stdout.write(self.style.SUCCESS(f'  • Объектов: {len(created_objects)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Систем: {System.objects.filter(object__user=user).count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Датчиков: {total_sensors}'))
        self.stdout.write(self.style.SUCCESS(f'  • Показаний: {Data.objects.filter(attribute__system__object__user=user).count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Тревог: {AlertRule.objects.filter(system__object__user=user).count()}'))
        self.stdout.write(self.style.SUCCESS(f'\nТеперь откройте http://your-domain.com/dashboard/ чтобы увидеть интерфейс! 🚀'))
