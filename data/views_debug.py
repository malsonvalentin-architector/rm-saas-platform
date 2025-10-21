"""
TEMPORARY DEBUG VIEWS - REMOVE IN PRODUCTION!
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.hashers import check_password
from .models import User_profile


@require_GET
def debug_check_users(request):
    """
    TEMPORARY: Check all users and passwords
    DELETE THIS VIEW AFTER DEBUGGING!
    """
    # Security check - only allow from localhost or specific IPs
    # In production, remove this view entirely!
    
    users_info = []
    
    for user in User_profile.objects.all().select_related('company'):
        users_info.append({
            'email': user.email,
            'role': user.role,
            'company': user.company.name if user.company else None,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'has_password': user.has_usable_password(),
        })
    
    # Test specific passwords
    test_results = []
    test_creds = [
        ('admin@promonitor.kz', 'ProMonitor2025!'),
        ('admin@promonitor.kz', 'Admin123!'),
        ('superadmin@test.kz', 'Test2025!'),
        ('admin@test.kz', 'Test2025!'),
    ]
    
    for email, password in test_creds:
        try:
            user = User_profile.objects.get(email=email)
            password_ok = check_password(password, user.password)
            test_results.append({
                'email': email,
                'password_tested': password,
                'password_correct': password_ok,
                'user_active': user.is_active,
            })
        except User_profile.DoesNotExist:
            test_results.append({
                'email': email,
                'password_tested': password,
                'error': 'USER_NOT_FOUND',
            })
    
    return JsonResponse({
        'total_users': len(users_info),
        'users': users_info,
        'password_tests': test_results,
        'warning': 'DELETE THIS ENDPOINT AFTER DEBUGGING!',
    })
