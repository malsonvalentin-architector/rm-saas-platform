"""
URL Configuration for ProMonitor
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Django Authentication (login, logout)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Data & Objects URLs
    # IMPORTANT: Data URLs must be first to avoid conflicts with home '/' and 'dashboard/'
    path('objects/', include('data.urls', namespace='data')),
    
    # Telegram Integration
    path('telegram/', include('teleg.urls', namespace='teleg')),
    
    # Home Dashboard (must be LAST to catch root URLs)
    path('', include('home.urls', namespace='home')),
]

# Static/Media files в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Кастомизация Admin панели
admin.site.site_header = "ProMonitor Administration"
admin.site.site_title = "ProMonitor Admin"
admin.site.index_title = "Система мониторинга ProMonitor"
