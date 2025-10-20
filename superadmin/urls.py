"""
URLs для Super Admin панели
"""

from django.urls import path, re_path
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Компании
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    re_path(r'^companies/(?P<pk>\d+)/$', views.CompanyDetailView.as_view(), name='company_detail'),
    
    # Подписки
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list'),
    re_path(r'^subscriptions/activate/(?P<pk>\d+)/$', views.subscription_activate, name='subscription_activate'),
    
    # Счета
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    
    # Статистика
    path('statistics/', views.statistics, name='statistics'),
]
