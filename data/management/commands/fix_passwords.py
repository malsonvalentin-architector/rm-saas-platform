# data/management/commands/fix_passwords.py
"""
Management command для исправления паролей пользователей
Usage: python manage.py fix_passwords
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Исправляет пароли пользователей на желаемые'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Обновление паролей пользователей...'))
        
        # Обновляем пароли
        password_updates = [
            ('superadmin@promonitor.kz', 'Super123!'),
            ('admin@promonitor.kz', 'Vika2025'),      # Желаемый пароль
            ('manager@promonitor.kz', 'Vika2025'),    # Желаемый пароль
            ('client@promonitor.kz', 'Client123!'),
        ]
        
        updated_count = 0
        for email, password in password_updates:
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Пароль обновлен для {email}')
                )
                updated_count += 1
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Пользователь {email} не найден')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Обновлено паролей: {updated_count}/{len(password_updates)}')
        )
        self.stdout.write(self.style.SUCCESS('🎉 Готово! Теперь можно входить с новыми паролями.'))
