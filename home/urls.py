"""
Home URLs
"""
from django.urls import path, include
from . import views
from .logout_views import custom_logout
from .test_views import system_status

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/v2/', include('home.urls_v2')),
    path('logout/', custom_logout, name='logout'),
    path('api/system-status/', system_status, name='system_status'),
]
