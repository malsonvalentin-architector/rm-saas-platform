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
    
    # Home Dashboard
    path('', include('home.urls', namespace='home')),
    
    # Data & Objects
    path('data/', include('data.urls', namespace='data')),
    
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
