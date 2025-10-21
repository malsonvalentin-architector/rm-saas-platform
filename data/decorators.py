"""
Phase 4.1: Permission Decorators for Function-Based Views
"""
from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, 'Access denied. Required role: ' + ', '.join(allowed_roles))
                raise PermissionDenied('User role not in allowed roles')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def superadmin_required(view_func):
    return role_required('superadmin')(view_func)


def admin_required(view_func):
    return role_required('superadmin', 'admin')(view_func)


def manager_required(view_func):
    return role_required('superadmin', 'admin', 'manager')(view_func)


def client_required(view_func):
    return role_required('client')(view_func)


def company_access_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        company_id = kwargs.get('company_id') or kwargs.get('pk')
        
        if not company_id:
            raise ValueError('company_access_required requires company_id or pk in URL kwargs')
        
        if request.user.role == 'superadmin':
            return view_func(request, *args, **kwargs)
        
        if request.user.company_id != int(company_id):
            messages.error(request, 'Access denied to this company')
            raise PermissionDenied('User does not have access to this company')
        
        return view_func(request, *args, **kwargs)
    return wrapper
