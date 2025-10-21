"""
Phase 4.1: Multi-Tenant Middleware
"""
from django.utils.deprecation import MiddlewareMixin


class CompanyAccessMiddleware(MiddlewareMixin):
    """Middleware for automatic filtering by user company"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            if request.user.role == 'superadmin':
                request.user_company = None
            else:
                request.user_company = request.user.company
        else:
            request.user_company = None
