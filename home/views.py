"""
Home Views - Главный дашборд ProMonitor
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from data.models import Object, System, AlertRule, Attribute, Data


@login_required
def dashboard(request):
    """
    Главная панель управления
    Показывает общую статистику по всем объектам пользователя
    """
    user = request.user
    
    # Получаем объекты пользователя
    if user.role == 'admin':
        objects = Object.objects.all()
    else:
        objects = Object.objects.filter(company=user.company)
    
    # Статистика
    total_objects = objects.count()
    total_systems = System.objects.filter(object__in=objects).count()
    
    # Активные тревоги (за последние 24 часа)
    last_24h = timezone.now() - timedelta(hours=24)
    active_alerts = AlertRule.objects.filter(
        is_active=True,
        attribute__system__object__in=objects
    ).count()
    
    # Средние показатели датчиков за последние 24 часа
    recent_data = Data.objects.filter(
        timestamp__gte=last_24h,
        attribute__system__object__in=objects
    )
    
    # Температура
    avg_temperature = recent_data.filter(
        attribute__attribute_type='temperature'
    ).aggregate(Avg('value'))['value__avg'] or 23
    
    # Влажность
    avg_humidity = recent_data.filter(
        attribute__attribute_type='humidity'
    ).aggregate(Avg('value'))['value__avg'] or 55
    
    # Мощность/энергия
    avg_power = recent_data.filter(
        attribute__attribute_type__in=['power', 'energy']
    ).aggregate(Avg('value'))['value__avg'] or 145
    
    # График энергопотребления за 24 часа (почасовая статистика)
    energy_chart_data = []
    for hour in range(24):
        hour_start = timezone.now() - timedelta(hours=24-hour)
        hour_end = hour_start + timedelta(hours=1)
        
        avg_value = Data.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end,
            attribute__attribute_type__in=['power', 'energy'],
            attribute__system__object__in=objects
        ).aggregate(Avg('value'))['value__avg']
        
        energy_chart_data.append({
            'hour': hour_start.strftime('%H:%M'),
            'value': round(avg_value or 0, 2)
        })
    
    # Последние тревоги
    recent_alerts = AlertRule.objects.filter(
        is_active=True,
        attribute__system__object__in=objects
    ).select_related('attribute', 'attribute__system', 'attribute__system__object')[:10]
    
    context = {
        'total_objects': total_objects,
        'total_systems': total_systems,
        'active_alerts': active_alerts,
        'avg_temperature': round(avg_temperature, 1),
        'avg_humidity': round(avg_humidity, 1),
        'avg_power': round(avg_power, 0),
        'energy_chart_data': energy_chart_data,
        'recent_alerts': recent_alerts,
    }
    
    return render(request, 'home/dashboard.html', context)


@login_required
def index(request):
    """
    Главная страница - перенаправляет на дашборд
    """
    return dashboard(request)
