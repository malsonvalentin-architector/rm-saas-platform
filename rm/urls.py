"""
URL Configuration for ProMonitor
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from home.test_views import system_status

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Django Authentication (login, logout)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Redirect /login/ to /accounts/login/ for convenience (MUST be before home.urls)
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='login_redirect'),
    
    # Telegram Integration
    path('telegram/', include('teleg.urls', namespace='teleg')),
    
    # Data & Objects (BEFORE home to avoid conflicts)
    path('', include('data.urls', namespace='data')),
    
    # Dashboard v2 - Modern Sidebar Interface
    path('dashboard/v2/', include('dashboard_v2.urls', namespace='dashboard_v2')),
    
    # Dashboard - New Clean Structure (legacy)
    path('dashboard/', include(('home.urls_v2', 'dashboard_v2_old'))),
    
    # Legacy redirects for old URLs
    path('dashboard/v2/', RedirectView.as_view(url='/dashboard/', permanent=True)),
    path('dashboard/main/', RedirectView.as_view(url='/dashboard/', permanent=True)),
    
    # Home - handles root '/' and logout
    path('', include('home.urls', namespace='home')),
    
    # System Status API (for testing)
    path('api/system-status/', system_status, name='system_status'),
]

# Static/Media files в режиме DEBUG
# NOTE: WhiteNoise handles static files in production
# Only serve media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Don't serve STATIC_URL in DEBUG - WhiteNoise handles it
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Кастомизация Admin панели
admin.site.site_header = "ProMonitor Administration"
admin.site.site_title = "ProMonitor Admin"
admin.site.index_title = "Система мониторинга ProMonitor"
