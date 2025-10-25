"""
ProMonitor V2 - Dashboard URL Configuration
URL patterns for enhanced dashboard with honeycomb visualization
"""

from django.urls import path
from . import views_v2
from . import views_v2_pages
from .ai_views import AIChatView, ai_rate_message, ai_chat_history, ai_clear_history, ai_status, ai_quick_analysis, ai_suggestions

app_name = 'dashboard_v2'  # Required for namespace in home/urls.py

urlpatterns = [
    # Main dashboard v2 - PROFESSIONAL VERSION
    path('', views_v2.dashboard_main_professional, name='dashboard_v2'),
    path('v2/', views_v2.dashboard_main_professional, name='main'),
    path('main/', views_v2.dashboard_main_professional, name='dashboard_main'),
    path('standalone/', views_v2.dashboard_v2_standalone, name='dashboard_v2_standalone'),
    
    # Navigation pages - NEW PROFESSIONAL PAGES
    path('buildings/', views_v2_pages.buildings_list, name='dashboard_v2_buildings'),
    path('sensors/', views_v2_pages.sensors_list, name='dashboard_v2_sensors'),
    path('alerts/', views_v2_pages.alerts_list, name='dashboard_v2_alerts'),
    path('reports/', views_v2_pages.reports_page, name='dashboard_v2_reports'),
    path('analytics/', views_v2_pages.analytics_page, name='dashboard_v2_analytics'),
    path('settings/', views_v2_pages.settings_page, name='dashboard_v2_settings'),
    path('users/', views_v2_pages.users_page, name='dashboard_v2_users'),
    
    # Building detail views
    path('building/<int:building_id>/', views_v2.building_detail_v2, name='building_detail'),
    
    # API endpoints for real-time updates
    path('api/honeycomb-data/', views_v2.honeycomb_data_api, name='honeycomb_data'),
    path('api/stats/', views_v2.dashboard_stats_api, name='dashboard_stats'),
    
    # User preferences
    path('api/v2/user/theme', views_v2.update_user_theme, name='update_theme'),
    
    # AI Assistant endpoints
    path('api/v2/ai/chat', AIChatView.as_view(), name='ai_chat'),
    path('api/ai-rate/', ai_rate_message, name='ai_rate'),
    path('api/ai-history/', ai_chat_history, name='ai_history'),
    path('api/ai-clear/', ai_clear_history, name='ai_clear'),
    path('api/ai-status/', ai_status, name='ai_status'),
    path('api/ai-analysis/', ai_quick_analysis, name='ai_analysis'),
    path('api/ai-suggestions/', ai_suggestions, name='ai_suggestions'),
]