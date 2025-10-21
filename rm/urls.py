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
    
    # Home Dashboard - MUST BE FIRST to handle '/' and 'dashboard/'
    path('', include('home.urls', namespace='home')),
    
    # Data & Objects - paths already include 'objects/' prefix
    # This will create: /objects/, /objects/<id>/, /sensors/<id>/history/
    path('', include('data.urls', namespace='data')),
    
    # Telegram Integration
    path('telegram/', include('teleg.urls', namespace='teleg')),
]

# Static/Media files в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Кастомизация Admin панели
admin.site.site_header = "ProMonitor Administration"
admin.site.site_title = "ProMonitor Admin"
admin.site.index_title = "Система мониторинга ProMonitor"
