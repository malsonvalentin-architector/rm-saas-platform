from django.urls import path
from . import views
from . import views_crud
from . import views_systems
from . import views_alerts
from . import views_actuators
from . import views_debug
from . import views_debug_template
from . import views_actuators_api

app_name = 'data'

urlpatterns = [
    # Objects list and dashboard
    path('objects/', views.object_list, name='object_list'),
    path('objects/<int:object_id>/', views.object_dashboard, name='object_dashboard'),
    
    # Global systems overview (Phase 4.2)
    path('systems/', views_systems.all_systems_overview, name='all_systems'),
    
    # Objects CRUD
    path('objects/create/', views_crud.object_create, name='object_create'),
    path('objects/<int:object_id>/edit/', views_crud.object_edit, name='object_edit'),
    path('objects/<int:object_id>/delete/', views_crud.object_delete, name='object_delete'),
    
    # Systems CRUD (Phase 4.2)
    path('objects/<int:object_id>/systems/', views_crud.system_list, name='system_list'),
    path('objects/<int:object_id>/systems/create/', views_crud.system_create, name='system_create'),
    path('systems/<int:system_id>/edit/', views_crud.system_edit, name='system_edit'),
    path('systems/<int:system_id>/delete/', views_crud.system_delete, name='system_delete'),
    
    # Sensors and realtime
    path('sensors/<int:sensor_id>/history/', views.sensor_history, name='sensor_history'),
    path('objects/<int:object_id>/realtime/', views.realtime_data, name='realtime_data'),
    
    # Alerts System (Phase 4.3)
    path('alerts/', views_alerts.alerts_list, name='alerts_list'),
    path('alerts/<int:alert_id>/', views_alerts.alert_detail, name='alert_detail'),
    path('alerts/<int:alert_id>/acknowledge/', views_alerts.alert_acknowledge, name='alert_acknowledge'),
    path('alerts/<int:alert_id>/resolve/', views_alerts.alert_resolve, name='alert_resolve'),
    path('alerts/<int:alert_id>/snooze/', views_alerts.alert_snooze, name='alert_snooze'),
    path('alerts/<int:alert_id>/comment/', views_alerts.alert_add_comment, name='alert_add_comment'),
    
    # Actuators (Phase 4.4)
    path('actuators/', views_actuators.actuators_list, name='actuators_list'),
    path('actuators/<int:actuator_id>/control/', views_actuators.actuator_control, name='actuator_control'),
    path('actuators/<int:actuator_id>/history/', views_actuators.actuator_history, name='actuator_history'),
    
    # Actuators API - Real-Time (Phase 4.5)
    path('api/actuators/live-stats/', views_actuators_api.actuators_live_stats, name='api_actuators_live_stats'),
    path('api/actuators/commands-timeline/', views_actuators_api.actuators_commands_timeline, name='api_commands_timeline'),
    path('api/actuators/activity-chart/', views_actuators_api.actuators_activity_chart, name='api_activity_chart'),
    path('api/actuators/by-type/', views_actuators_api.actuators_by_type, name='api_actuators_by_type'),
    
    # DEBUG: URL patterns inspector
    path('debug/urls/', views.debug_urls, name='debug_urls'),
    path('debug/actuators/', views_debug.debug_actuators_count, name='debug_actuators'),
    path('debug/template/', views_debug_template.debug_template_source, name='debug_template'),
]
