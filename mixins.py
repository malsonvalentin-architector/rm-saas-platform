"""
Phase 4.1: Permission Mixins for Class-Based Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []
    
    def test_func(self):
        if not self.allowed_roles:
            raise ValueError('allowed_roles must be defined in the view')
        
        user_role = self.request.user.role
        has_access = user_role in self.allowed_roles
        
        if not has_access:
            messages.error(self.request, 'Access denied. Required role: ' + ', '.join(self.allowed_roles))
        
        return has_access
    
    def handle_no_permission(self):
        raise PermissionDenied('User role not in allowed roles')


class SuperadminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin']


class CompanyAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin', 'admin']


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin', 'admin', 'manager']


class ClientRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['client']


class CompanyAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.role == 'superadmin':
            return queryset
        
        if hasattr(queryset.model, 'company'):
            return queryset.filter(company=self.request.user.company)
        
        return queryset


class ObjectOwnerMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        if self.request.user.role == 'superadmin':
            return obj
        
        if hasattr(obj, 'company') and obj.company != self.request.user.company:
            messages.error(self.request, 'Access denied to this object')
            raise PermissionDenied('User does not have access to this object')
        
        return obj
