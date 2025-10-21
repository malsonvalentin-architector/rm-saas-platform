from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('objects/', views.object_list, name='object_list'),
    path('objects/<int:object_id>/', views.object_dashboard, name='object_dashboard'),
    path('sensors/<int:sensor_id>/history/', views.sensor_history, name='sensor_history'),
    path('objects/<int:object_id>/realtime/', views.realtime_data, name='realtime_data'),
]
