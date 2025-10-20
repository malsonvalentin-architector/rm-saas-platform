"""rm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from home.views import RegisterView

urlpatterns = [
    # Admin panels
    path('admin/', admin.site.urls),
    path('superadmin/', include('superadmin.urls')),
    
    # Main apps
    path('data/', include('data.urls')),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Home
    path('', TemplateView.as_view(template_name='home/main.html'), name='home'),
]
