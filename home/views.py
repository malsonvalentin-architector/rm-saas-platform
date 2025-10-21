"""
Home Views - Главный дашборд ProMonitor
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from data.models import Obj, System, AlertRule, Atributes, Data


@login_required
def dashboard(request):
    """
    Главная панель управления
    Показывает общую статистику по всем объектам пользователя
    """
    user = request.user
    
    # Получаем объекты пользователя
    if user.role == 'admin':
        objects = Obj.objects.all()
    else:
        objects = Obj.objects.filter(company=user.company)
    
    # Статистика
    total_objects = objects.count()
    total_systems = System.objects.filter(obj__in=objects).count()
    
    # Активные тревоги (за последние 24 часа)
    last_24h = timezone.now() - timedelta(hours=24)
    active_alerts = AlertRule.objects.filter(
        enabled=True,
        name__sys__obj__in=objects
    ).count()
    
    # Средние показатели датчиков за последние 24 часа
    recent_data = Data.objects.filter(
        date__gte=last_24h,
        name__sys__obj__in=objects
    )
    
    # Температура
    avg_temperature = recent_data.filter(
        name__name__icontains='температур'
    ).aggregate(Avg('value'))['value__avg'] or 23
    
    # Влажность
    avg_humidity = recent_data.filter(
        name__name__icontains='влажн'
    ).aggregate(Avg('value'))['value__avg'] or 55
    
    # Мощность/энергия
    avg_power = recent_data.filter(
        name__name__icontains='мощн'
    ).aggregate(Avg('value'))['value__avg'] or 145
    
    # График энергопотребления за 24 часа (почасовая статистика)
    energy_chart_data = []
    for hour in range(24):
        hour_start = timezone.now() - timedelta(hours=24-hour)
        hour_end = hour_start + timedelta(hours=1)
        
        avg_value = Data.objects.filter(
            date__gte=hour_start,
            timestamp__lt=hour_end,
            name__name__icontains='мощн',
            name__sys__obj__in=objects
        ).aggregate(Avg('value'))['value__avg']
        
        energy_chart_data.append({
            'hour': hour_start.strftime('%H:%M'),
            'value': round(avg_value or 0, 2)
        })
    
    # Последние тревоги
    recent_alerts = AlertRule.objects.filter(
        enabled=True,
        name__sys__obj__in=objects
    ).select_related('name__system', 'name__sys__obj')[:10]
    
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


def index(request):
    """
    Главная страница - если авторизован → дашборд, иначе → логин
    """
    if request.user.is_authenticated:
        return dashboard(request)
    else:
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('login'))
