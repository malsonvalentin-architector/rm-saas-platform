"""
Временные view для тестирования и проверки системы
"""
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from data.models import Company

User = get_user_model()


def system_status(request):
    """Проверка статуса системы и пользователей"""
    
    # Подсчитываем пользователей по ролям
    users_by_role = {}
    for role in ['superadmin', 'admin', 'manager', 'client']:
        count = User.objects.filter(role=role).count()
        users_by_role[role] = count
    
    # Проверяем наличие тестовых пользователей
    test_users = {}
    for email in ['superadmin@promonitor.kz', 'admin@promonitor.kz', 
                  'manager@promonitor.kz', 'client@promonitor.kz']:
        exists = User.objects.filter(email=email).exists()
        test_users[email] = 'exists' if exists else 'missing'
    
    # Информация о компаниях
    companies = {
        'total': Company.objects.count(),
        'active': Company.objects.filter(is_active=True).count(),
    }
    
    return JsonResponse({
        'status': 'ok',
        'users': {
            'total': User.objects.count(),
            'by_role': users_by_role,
            'test_accounts': test_users,
        },
        'companies': companies,
        'database': 'connected',
    })
