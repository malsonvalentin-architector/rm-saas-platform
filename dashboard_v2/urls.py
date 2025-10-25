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
    path('map/', views.map_page, name='map'),  # NEW
    path('settings/', views.settings_page, name='settings'),
    
    # API endpoints
    path('api/metrics/', views.api_dashboard_metrics, name='api_metrics'),
    path('api/control/devices/', views.api_control_devices, name='api_devices'),
    path('api/control/command/', views.api_control_command, name='api_command'),
    path('api/alerts/', views.api_alerts_list, name='api_alerts'),
    path('api/analytics/stats/', views.api_analytics_stats, name='api_stats'),
    
    # Settings API (NEW)
    path('api/settings/profile/', views.api_settings_profile, name='api_settings_profile'),
    path('api/settings/password/', views.api_settings_password, name='api_settings_password'),
    path('api/settings/preferences/', views.api_settings_preferences, name='api_settings_preferences'),
    
    # Alerts API (NEW)
    path('api/alerts/acknowledge/', views.api_alert_acknowledge, name='api_alert_acknowledge'),
    path('api/alerts/resolve/', views.api_alert_resolve, name='api_alert_resolve'),
]
