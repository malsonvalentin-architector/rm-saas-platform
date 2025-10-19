"""
URLs для Super Admin панели
"""

from django.conf.urls import url
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Dashboard
    url(r'^$', views.dashboard, name='dashboard')
    
    # Компании
    url(r'^companies/', views.CompanyListView.as_view(), name='company_list')
    url(r'^companies/(?P<pk>\d+)/', views.CompanyDetailView.as_view(), name='company_detail')
    
    # Подписки
    url(r'^subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list')
    url(r'^subscriptions/activate/(?P<pk>\d+)/', views.subscription_activate, name='subscription_activate')
    
    # Счета
    url(r'^invoices/', views.InvoiceListView.as_view(), name='invoice_list')
    
    # Статистика
    url(r'^statistics/', views.statistics, name='statistics')
]
