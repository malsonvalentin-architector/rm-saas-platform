"""
Phase 4.1: Multi-Tenant Middleware
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import redirect_to_login
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


class RoleBasedRedirectMiddleware(MiddlewareMixin):
    """Middleware for role-based redirects"""
    
    PUBLIC_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/password_reset/',
        '/accounts/password_reset/done/',
        '/static/',
        '/media/',
        '/admin/',
    ]
    
    ROLE_HOME_PAGES = {
        'superadmin': '/dashboard/',
        'admin': '/dashboard/',
        'manager': '/objects/',
        'client': '/portal/',
    }
    
    def process_request(self, request):
        if any(request.path.startswith(url) for url in self.PUBLIC_URLS):
            return None
        
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        
        if request.path == '/' or request.path == '/dashboard/':
            home_page = self.ROLE_HOME_PAGES.get(request.user.role, '/dashboard/')
            if request.path != home_page:
                return redirect(home_page)
        
        return None
