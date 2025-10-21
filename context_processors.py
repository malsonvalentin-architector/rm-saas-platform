"""
Phase 4.1: Context Processors
"""


def user_context(request):
    if not request.user.is_authenticated:
        return {}
    
    return {
        'user_role': request.user.role,
        'user_company': request.user.company,
        'is_superadmin': request.user.role == 'superadmin',
        'is_admin': request.user.role in ['superadmin', 'admin'],
        'is_manager': request.user.role in ['superadmin', 'admin', 'manager'],
        'is_client': request.user.role == 'client',
        'can_manage_objects': request.user.can_manage_objects(),
        'can_view_billing': request.user.can_view_billing(),
        'can_manage_subscription': request.user.can_manage_subscription(),
        'can_manage_users': request.user.can_manage_users(),
    }


def role_display(request):
    if not request.user.is_authenticated:
        return {}
    
    role_names = {
        'superadmin': 'Superadministrator',
        'admin': 'Company Administrator',
        'manager': 'Manager',
        'client': 'Client',
    }
    
    role_colors = {
        'superadmin': 'danger',
        'admin': 'primary',
        'manager': 'warning',
        'client': 'success',
    }
    
    return {
        'role_display_name': role_names.get(request.user.role, request.user.role),
        'role_badge_color': role_colors.get(request.user.role, 'secondary'),
    }
