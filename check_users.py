import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')
django.setup()

from data.models import User_profile, Company

print("\n=== ВСЕ ПОЛЬЗОВАТЕЛИ В БАЗЕ ===\n")
users = User_profile.objects.all().select_related('company')

for user in users:
    print(f"Email: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Company: {user.company.name if user.company else 'NO COMPANY'}")
    print(f"  is_active: {user.is_active}")
    print(f"  is_staff: {user.is_staff}")
    print(f"  has_usable_password: {user.has_usable_password()}")
    print()

print(f"\nВСЕГО ПОЛЬЗОВАТЕЛЕЙ: {users.count()}")

# Проверка конкретных тестовых пользователей
test_emails = ['admin@promonitor.kz', 'superadmin@test.kz', 'admin@test.kz']
print("\n=== ПРОВЕРКА ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ ===\n")
for email in test_emails:
    try:
        user = User_profile.objects.get(email=email)
        print(f"✅ {email} - EXISTS (role: {user.role})")
    except User_profile.DoesNotExist:
        print(f"❌ {email} - NOT FOUND")
