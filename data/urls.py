from django.urls import path
from . import views
from . import views_crud
from . import views_systems
from . import views_alerts

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
    
    # DEBUG: URL patterns inspector
    path('debug/urls/', views.debug_urls, name='debug_urls'),
]
