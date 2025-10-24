"""
ProMonitor V2 - Dashboard URL Configuration
URL patterns for enhanced dashboard with honeycomb visualization
"""

from django.urls import path
from . import views_v2

app_name = 'dashboard_v2'

urlpatterns = [
    # Main dashboard v2
    path('', views_v2.dashboard_v2, name='main'),
    path('v2/', views_v2.dashboard_v2, name='main_v2'),
    
    # Building detail views
    path('building/<int:building_id>/', views_v2.building_detail_v2, name='building_detail'),
    
    # API endpoints for real-time updates
    path('api/honeycomb-data/', views_v2.honeycomb_data_api, name='honeycomb_data'),
    path('api/stats/', views_v2.dashboard_stats_api, name='dashboard_stats'),
    
    # User preferences
    path('api/update-theme/', views_v2.update_user_theme, name='update_theme'),
]