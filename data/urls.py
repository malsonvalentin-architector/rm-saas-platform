from django.urls import path
from . import views
from . import views_crud

app_name = 'data'

urlpatterns = [
    # Objects list and dashboard
    path('objects/', views.object_list, name='object_list'),
    path('objects/<int:object_id>/', views.object_dashboard, name='object_dashboard'),
    
    # Objects CRUD
    path('objects/create/', views_crud.object_create, name='object_create'),
    path('objects/<int:object_id>/edit/', views_crud.object_edit, name='object_edit'),
    path('objects/<int:object_id>/delete/', views_crud.object_delete, name='object_delete'),
    
    # Sensors and realtime
    path('sensors/<int:sensor_id>/history/', views.sensor_history, name='sensor_history'),
    path('objects/<int:object_id>/realtime/', views.realtime_data, name='realtime_data'),
]
