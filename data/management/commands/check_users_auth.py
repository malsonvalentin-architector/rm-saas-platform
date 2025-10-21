"""
Management command для проверки пользователей и их паролей
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import check_password
from data.models import User_profile


class Command(BaseCommand):
    help = 'Check users and test authentication'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ ===\n'))
        
        users = User_profile.objects.all().select_related('company')
        
        self.stdout.write(f'Всего пользователей в БД: {users.count()}\n')
        
        for user in users:
            self.stdout.write(f'\n📧 Email: {user.email}')
            self.stdout.write(f'   Role: {user.role}')
            self.stdout.write(f'   Company: {user.company.name if user.company else "❌ NO COMPANY"}')
            self.stdout.write(f'   is_active: {"✅" if user.is_active else "❌"} {user.is_active}')
            self.stdout.write(f'   is_staff: {"✅" if user.is_staff else "❌"} {user.is_staff}')
            self.stdout.write(f'   has_usable_password: {"✅" if user.has_usable_password() else "❌"} {user.has_usable_password()}')
        
        # Проверка конкретных тестовых паролей
        self.stdout.write(self.style.SUCCESS('\n\n=== ПРОВЕРКА ТЕСТОВЫХ ПАРОЛЕЙ ===\n'))
        
        test_creds = [
            ('admin@promonitor.kz', 'ProMonitor2025!'),
            ('admin@promonitor.kz', 'Admin123!'),
            ('superadmin@test.kz', 'Test2025!'),
            ('admin@test.kz', 'Test2025!'),
            ('manager@test.kz', 'Test2025!'),
            ('client@test.kz', 'Test2025!'),
        ]
        
        for email, password in test_creds:
            try:
                user = User_profile.objects.get(email=email)
                password_ok = check_password(password, user.password)
                
                if password_ok:
                    self.stdout.write(self.style.SUCCESS(f'✅ {email} / {password} - OK'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ {email} / {password} - WRONG PASSWORD'))
                    
            except User_profile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠️  {email} - USER NOT FOUND'))
        
        # Проверка методов роли
        self.stdout.write(self.style.SUCCESS('\n\n=== ПРОВЕРКА МЕТОДОВ РОЛЕЙ ===\n'))
        
        for user in users[:4]:  # Первые 4 пользователя
            self.stdout.write(f'\n{user.email} ({user.role}):')
            self.stdout.write(f'  is_superadmin(): {user.is_superadmin()}')
            self.stdout.write(f'  is_company_admin(): {user.is_company_admin()}')
            self.stdout.write(f'  can_manage_objects(): {user.can_manage_objects()}')
            self.stdout.write(f'  can_view_billing(): {user.can_view_billing()}')
        
        self.stdout.write(self.style.SUCCESS('\n\n=== ПРОВЕРКА ЗАВЕРШЕНА ===\n'))
