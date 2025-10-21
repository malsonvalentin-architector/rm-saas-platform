"""
Management command для вывода списка всех пользователей
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import check_password
from data.models import User_profile


class Command(BaseCommand):
    help = 'List all users with their details'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*70)
        self.stdout.write('                    СПИСОК ПОЛЬЗОВАТЕЛЕЙ')
        self.stdout.write('='*70 + '\n')
        
        users = User_profile.objects.all().select_related('company').order_by('role', 'email')
        
        if not users.exists():
            self.stdout.write(self.style.ERROR('❌ ПОЛЬЗОВАТЕЛЕЙ НЕТ В БАЗЕ!'))
            return
        
        self.stdout.write(f'Всего пользователей: {users.count()}\n')
        
        for i, user in enumerate(users, 1):
            self.stdout.write(f'\n[{i}] {user.email}')
            self.stdout.write(f'    Роль: {user.role}')
            self.stdout.write(f'    Компания: {user.company.name if user.company else "❌ НЕТ"}')
            self.stdout.write(f'    Активен: {"✅" if user.is_active else "❌"} ({user.is_active})')
            self.stdout.write(f'    Персонал: {"✅" if user.is_staff else "❌"} ({user.is_staff})')
            self.stdout.write(f'    Superuser: {"✅" if user.is_superuser else "❌"} ({user.is_superuser})')
            self.stdout.write(f'    Пароль установлен: {"✅" if user.has_usable_password() else "❌"}')
        
        # Проверка тестовых паролей
        self.stdout.write('\n' + '='*70)
        self.stdout.write('                 ПРОВЕРКА ПАРОЛЕЙ')
        self.stdout.write('='*70 + '\n')
        
        test_passwords = [
            ('admin@promonitor.kz', 'ProMonitor2025!'),
            ('admin@promonitor.kz', 'Admin123!'),
            ('superadmin@test.kz', 'Test2025!'),
            ('admin@test.kz', 'Test2025!'),
            ('manager@test.kz', 'Test2025!'),
            ('client@test.kz', 'Test2025!'),
        ]
        
        for email, password in test_passwords:
            try:
                user = User_profile.objects.get(email=email)
                is_correct = check_password(password, user.password)
                
                status = '✅ ПРАВИЛЬНЫЙ' if is_correct else '❌ НЕПРАВИЛЬНЫЙ'
                self.stdout.write(f'{status} | {email} / {password}')
                
                if not is_correct:
                    # Попробуем другие распространённые пароли
                    other_passwords = ['admin', 'Admin123!', 'ProMonitor2025!', 'Test2025!']
                    for other_pwd in other_passwords:
                        if check_password(other_pwd, user.password):
                            self.stdout.write(f'           💡 ПРАВИЛЬНЫЙ ПАРОЛЬ: {other_pwd}')
                            break
                
            except User_profile.DoesNotExist:
                self.stdout.write(f'⚠️  НЕ НАЙДЕН | {email}')
        
        self.stdout.write('\n' + '='*70 + '\n')
