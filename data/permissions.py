"""
Phase 4.1: Role-Based Permissions Decorators
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(*allowed_roles):
    """
    Decorator to restrict view access based on user role.
    
    Usage:
        @role_required('superadmin', 'admin')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_role = getattr(request.user, 'role', None)
            
            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f'У вас нет доступа к этому разделу. Требуется роль: {", ".join(allowed_roles)}'
                )
                return redirect('home:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def can_create(user):
    """Check if user can create objects"""
    if not hasattr(user, 'role'):
        return False
    return user.role in ['superadmin', 'admin', 'manager']


def can_edit(user):
    """Check if user can edit objects"""
    if not hasattr(user, 'role'):
        return False
    return user.role in ['superadmin', 'admin', 'manager']


def can_delete(user):
    """Check if user can delete objects"""
    if not hasattr(user, 'role'):
        return False
    return user.role in ['superadmin', 'admin']


def is_read_only(user):
    """Check if user has read-only access"""
    if not hasattr(user, 'role'):
        return True
    return user.role == 'client'


def get_user_permissions(user):
    """
    Get dictionary of user permissions based on role.
    
    Returns dict with boolean flags:
    {
        'can_view': True/False,
        'can_create': True/False,
        'can_edit': True/False,
        'can_delete': True/False,
        'is_read_only': True/False,
    }
    """
    if not hasattr(user, 'role'):
        return {
            'can_view': False,
            'can_create': False,
            'can_edit': False,
            'can_delete': False,
            'is_read_only': True,
        }
    
    role = user.role
    
    permissions = {
        'superadmin': {
            'can_view': True,
            'can_create': True,
            'can_edit': True,
            'can_delete': True,
            'is_read_only': False,
            'can_view_all_companies': True,
            'can_manage_users': True,
            'can_manage_companies': True,
        },
        'admin': {
            'can_view': True,
            'can_create': True,
            'can_edit': True,
            'can_delete': True,
            'is_read_only': False,
            'can_view_all_companies': False,
            'can_manage_users': True,
            'can_manage_companies': False,
        },
        'manager': {
            'can_view': True,
            'can_create': True,
            'can_edit': True,
            'can_delete': False,
            'is_read_only': False,
            'can_view_all_companies': False,
            'can_manage_users': False,
            'can_manage_companies': False,
        },
        'client': {
            'can_view': True,
            'can_create': False,
            'can_edit': False,
            'can_delete': False,
            'is_read_only': True,
            'can_view_all_companies': False,
            'can_manage_users': False,
            'can_manage_companies': False,
        },
    }
    
    return permissions.get(role, permissions['client'])
