"""
URLs для Super Admin панели
"""

from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Компании
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    
    # Подписки
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('subscriptions/activate/<int:pk>/', views.subscription_activate, name='subscription_activate'),
    
    # Счета
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    
    # Статистика
    path('statistics/', views.statistics, name='statistics'),
]
