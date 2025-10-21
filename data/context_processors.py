"""
Phase 4.1: Context Processors
"""


def user_context(request):
    """Add user role and permissions to template context"""
    if not request.user.is_authenticated:
        return {}
    
    try:
        # Safely get role (fallback to None if not exists)
        user_role = getattr(request.user, 'role', None)
        user_company = getattr(request.user, 'company', None)
        
        return {
            'user_role': user_role,
            'user_company': user_company,
            'is_superadmin': user_role == 'superadmin',
            'is_admin': user_role in ['superadmin', 'admin'],
            'is_manager': user_role in ['superadmin', 'admin', 'manager'],
            'is_client': user_role == 'client',
            'can_manage_objects': getattr(request.user, 'can_manage_objects', lambda: False)(),
            'can_view_billing': getattr(request.user, 'can_view_billing', lambda: False)(),
            'can_manage_subscription': getattr(request.user, 'can_manage_subscription', lambda: False)(),
            'can_manage_users': getattr(request.user, 'can_manage_users', lambda: False)(),
        }
    except Exception:
        # Fallback if any error occurs
        return {}


def role_display(request):
    """Add role display name and color to template context"""
    if not request.user.is_authenticated:
        return {}
    
    try:
        user_role = getattr(request.user, 'role', None)
        
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
            'role_display_name': role_names.get(user_role, user_role or 'User'),
            'role_badge_color': role_colors.get(user_role, 'secondary'),
        }
    except Exception:
        return {
            'role_display_name': 'User',
            'role_badge_color': 'secondary',
        }
