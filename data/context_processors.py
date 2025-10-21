"""
Phase 4.1: Context Processors
"""
from .permissions import get_user_permissions


def user_context(request):
    """Add user role and permissions to template context"""
    if not request.user.is_authenticated:
        return {}
    
    try:
        # Safely get role (fallback to None if not exists)
        user_role = getattr(request.user, 'role', None)
        user_company = getattr(request.user, 'company', None)
        
        # Get full permissions dict
        perms = get_user_permissions(request.user)
        
        return {
            'user_role': user_role,
            'user_company': user_company,
            'is_superadmin': user_role == 'superadmin',
            'is_admin': user_role in ['superadmin', 'admin'],
            'is_manager': user_role in ['superadmin', 'admin', 'manager'],
            'is_client': user_role == 'client',
            # Add all permissions from get_user_permissions
            'user_permissions': perms,
            'can_view': perms.get('can_view', False),
            'can_create': perms.get('can_create', False),
            'can_edit': perms.get('can_edit', False),
            'can_delete': perms.get('can_delete', False),
            'is_read_only': perms.get('is_read_only', True),
            'can_manage_users': perms.get('can_manage_users', False),
            'can_manage_companies': perms.get('can_manage_companies', False),
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
