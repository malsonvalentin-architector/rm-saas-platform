"""
Dashboard v2 URL Configuration
Modern sidebar-based dashboard for ProMonitor
"""
from django.urls import path
from . import views

app_name = 'dashboard_v2'

urlpatterns = [
    # Main pages
    path('', views.dashboard_home, name='dashboard'),
    path('', views.dashboard_home, name='home'),  # Alias for compatibility
    path('control/', views.control_panel, name='control'),
    path('alerts/', views.alerts_page, name='alerts'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('objects/', views.objects_page, name='objects'),
    path('settings/', views.settings_page, name='settings'),
    
    # API endpoints
    path('api/metrics/', views.api_dashboard_metrics, name='api_metrics'),
    path('api/control/devices/', views.api_control_devices, name='api_devices'),
    path('api/control/command/', views.api_control_command, name='api_command'),
    path('api/alerts/', views.api_alerts_list, name='api_alerts'),
    path('api/analytics/stats/', views.api_analytics_stats, name='api_stats'),
]
