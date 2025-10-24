"""
Management command для создания пользователей ProMonitor
Usage: python manage.py create_users_final
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.models import Company

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает пользователей ProMonitor с нужными паролями и правами'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n👥 Создание пользователей ProMonitor...\n'))
        
        # Получаем или создаем компанию для demo пользователей
        demo_company, _ = Company.objects.get_or_create(
            name='ProMonitor Demo',
            defaults={
                'description': 'Демонстрационная компания',
                'is_active': True
            }
        )
        
        # Список пользователей для создания
        users_data = [
            {
                'email': 'superadmin@promonitor.kz',
                'password': 'Super123!',
                'role': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'company': None,  # Superadmin не привязан к компании
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'admin@promonitor.kz',
                'password': 'Vika2025',
                'role': 'admin',
                'first_name': 'Vika',
                'last_name': 'Administrator',
                'company': demo_company,
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'email': 'manager@promonitor.kz',
                'password': 'Vika2025',
                'role': 'manager',
                'first_name': 'Vika',
                'last_name': 'Manager',
                'company': demo_company,
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'client@promonitor.kz',
                'password': 'Client123!',
                'role': 'client',
                'first_name': 'Client',
                'last_name': 'User',
                'company': demo_company,
                'is_staff': False,
                'is_superuser': False,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in users_data:
            email = user_data['email']
            password = user_data.pop('password')
            
            # Проверяем существует ли пользователь
            try:
                user = User.objects.get(email=email)
                # Обновляем существующего пользователя
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Обновлен: {email} (роль: {user_data["role"]})')
                )
                updated_count += 1
                
            except User.DoesNotExist:
                # Создаем нового пользователя
                user = User(**user_data)
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Создан: {email} (роль: {user_data["role"]})')
                )
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Готово!'))
        self.stdout.write(self.style.SUCCESS(f'   Создано: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Обновлено: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'\n📋 Учетные данные:'))
        self.stdout.write('   superadmin@promonitor.kz / Super123! (все права)')
        self.stdout.write('   admin@promonitor.kz / Vika2025 (администратор компании)')
        self.stdout.write('   manager@promonitor.kz / Vika2025 (менеджер)')
        self.stdout.write('   client@promonitor.kz / Client123! (клиент)\n')
