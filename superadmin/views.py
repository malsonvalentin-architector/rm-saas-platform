"""
SUPER ADMIN ПАНЕЛЬ
Управление всеми компаниями, пользователями, подписками
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from data.models import (
    Company, User_profile, SubscriptionPlan, Subscription, 
    Invoice, Obj, System, Data
)


def is_superuser(user):
    """Проверка, что пользователь - суперадмин"""
    return user.is_superuser


# ============================================================================
# DASHBOARD
# ============================================================================

@user_passes_test(is_superuser)
def dashboard(request):
    """Главная страница супер-админ панели"""
    
    # Статистика
    stats = {
        'total_companies': Company.objects.count(),
        'active_companies': Company.objects.filter(
            subscription_status='active',
            is_active=True
        ).count(),
        'trial_companies': Company.objects.filter(
            subscription_status='trial'
        ).count(),
        'total_users': User_profile.objects.count(),
        'total_objects': Obj.objects.count(),
        'total_systems': System.objects.count(),
        'total_revenue_monthly': Subscription.objects.filter(
            is_paid=True,
            billing_period='monthly'
        ).aggregate(
            total=Sum('plan__price_monthly')
        )['total'] or 0,
    }
    
    # Последние компании
    recent_companies = Company.objects.order_by('-created_at')[:10]
    
    # Истекающие подписки (в течение 7 дней)
    expiring_soon = Company.objects.filter(
        subscription_expires_at__lte=timezone.now() + timedelta(days=7),
        subscription_expires_at__gte=timezone.now(),
        subscription_status='active'
    ).order_by('subscription_expires_at')
    
    # Неоплаченные счета
    unpaid_invoices = Invoice.objects.filter(
        status='pending'
    ).order_by('due_date')[:10]
    
    context = {
        'stats': stats,
        'recent_companies': recent_companies,
        'expiring_soon': expiring_soon,
        'unpaid_invoices': unpaid_invoices,
    }
    
    return render(request, 'superadmin/dashboard.html', context)


# ============================================================================
# КОМПАНИИ
# ============================================================================

@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CompanyListView(ListView):
    """Список всех компаний"""
    model = Company
    template_name = 'superadmin/company_list.html'
    context_object_name = 'companies'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтры
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(subscription_status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_email__icontains=search) |
                Q(inn__icontains=search)
            )
        
        return queryset.order_by('-created_at')


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CompanyDetailView(DetailView):
    """Детальная информация о компании"""
    model = Company
    template_name = 'superadmin/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object
        
        # Статистика компании
        context['users'] = User_profile.objects.filter(company=company)
        context['objects'] = Obj.objects.filter(company=company)
        context['systems'] = System.objects.filter(obj__company=company)
        
        # Подписка
        try:
            context['subscription'] = company.subscription
        except:
            context['subscription'] = None
        
        # Счета
        context['invoices'] = Invoice.objects.filter(company=company).order_by('-created_at')[:10]
        
        # История данных (последние записи)
        context['recent_data'] = Data.objects.filter(
            name__sys__obj__company=company
        ).order_by('-date')[:20]
        
        return context


# ============================================================================
# ПОДПИСКИ
# ============================================================================

@method_decorator(user_passes_test(is_superuser), name='dispatch')
class SubscriptionListView(ListView):
    """Список всех подписок"""
    model = Subscription
    template_name = 'superadmin/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 50
    
    def get_queryset(self):
        return super().get_queryset().select_related('company', 'plan').order_by('-created_at')


@user_passes_test(is_superuser)
def subscription_activate(request, pk):
    """Активировать подписку компании"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        billing_period = request.POST.get('billing_period', 'monthly')
        
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
        
        # Создаем или обновляем подписку
        subscription, created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan': plan,
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=30 if billing_period == 'monthly' else 365),
                'billing_period': billing_period,
                'is_paid': True,
            }
        )
        
        if not created:
            subscription.plan = plan
            subscription.start_date = timezone.now().date()
            subscription.end_date = timezone.now().date() + timedelta(days=30 if billing_period == 'monthly' else 365)
            subscription.billing_period = billing_period
            subscription.is_paid = True
            subscription.cancelled_at = None
            subscription.save()
        
        # Обновляем статус компании
        company.subscription_status = 'active'
        company.subscription_expires_at = subscription.end_date
        company.save()
        
        return redirect('superadmin:company_detail', pk=company.pk)
    
    # GET запрос - показываем форму
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'superadmin/subscription_activate.html', {
        'company': company,
        'plans': plans,
    })


# ============================================================================
# СЧЕТА
# ============================================================================

@method_decorator(user_passes_test(is_superuser), name='dispatch')
class InvoiceListView(ListView):
    """Список всех счетов"""
    model = Invoice
    template_name = 'superadmin/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтры
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('company', 'subscription').order_by('-created_at')


# ============================================================================
# СТАТИСТИКА
# ============================================================================

@user_passes_test(is_superuser)
def statistics(request):
    """Детальная статистика платформы"""
    
    # Рост компаний по месяцам
    companies_growth = Company.objects.extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Распределение по тарифам
    plans_distribution = Subscription.objects.filter(
        is_paid=True
    ).values('plan__name').annotate(count=Count('id'))
    
    # Топ-10 компаний по системам
    top_companies = Company.objects.annotate(
        systems_count=Count('obj__system')
    ).order_by('-systems_count')[:10]
    
    context = {
        'companies_growth': list(companies_growth),
        'plans_distribution': list(plans_distribution),
        'top_companies': top_companies,
    }
    
    return render(request, 'superadmin/statistics.html', context)
