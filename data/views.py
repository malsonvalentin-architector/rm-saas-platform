from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Obj, System, Atributes, Data, AlertRule


@login_required
def object_list(request):
    """Список всех объектов компании пользователя"""
    # Phase 4.1: Filter by company instead of user
    if request.user.role == 'superadmin':
        objects = Obj.objects.all()
    else:
        objects = Obj.objects.filter(company=request.user.company)
    
    # FIXED: AlertRule связан через Obj → System → Atributes → AlertRule
    # Правильный путь: system (related_name='system') → atributes (related_name='atributes') → alertrule_set
    objects = objects.annotate(
        system_count=Count('system'),
        alert_count=Count('system__atributes__alertrule', filter=Q(system__atributes__alertrule__enabled=True))
    )
    
    # Filter systems and alerts by company too
    if request.user.role == 'superadmin':
        total_systems = System.objects.count()
        total_alerts = AlertRule.objects.filter(enabled=True).count()
    else:
        total_systems = System.objects.filter(obj__company=request.user.company).count()
        total_alerts = AlertRule.objects.filter(company=request.user.company, enabled=True).count()
    
    context = {
        'objects': objects,
        'total_objects': objects.count(),
        'total_systems': total_systems,
        'total_alerts': total_alerts,
    }
    
    return render(request, 'data/object_list.html', context)


@login_required
def object_dashboard(request, object_id):
    """Детальный дашборд объекта с планом этажа"""
    # Phase 4.1: Check company access
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    # Получаем все системы объекта
    systems = System.objects.filter(obj=obj).prefetch_related('atributes_set')
    
    # Получаем последние данные по всем датчикам
    sensors_data = []
    for system in systems:
        for attr in system.atributes_set.all():
            latest = Data.objects.filter(name=attr).order_by('-date').first()
            if latest:
                sensors_data.append({
                    'id': attr.id,
                    'name': attr.name,
                    'system': system.name,
                    'value': latest.value,
                    'unit': attr.uom or '',
                    'timestamp': latest.date,
                    # 'x_position': 50,  # TODO: добавить в модель  # Позиция на плане (%)
                    # 'y_position': 50,  # TODO: добавить в модель
                    'room': 'Общая зона',
                })
    
    # Статистика по объекту
    # FIXED: AlertRule.company вместо несуществующего sys__obj
    stats = {
        'systems_count': systems.count(),
        'sensors_count': sum(s.atributes_set.count() for s in systems),
        'active_alerts': AlertRule.objects.filter(company=obj.company, enabled=True).count(),
    }
    
    # Средние показатели по типам датчиков
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    avg_temperature = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='температур',
        date__gte=last_24h
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    avg_humidity = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='влажн',
        date__gte=last_24h
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    avg_power = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='мощн',
        date__gte=last_24h
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    # Активные тревоги
    # FIXED: AlertRule.company вместо несуществующего sys__obj
    alerts = AlertRule.objects.filter(
        company=obj.company,
        enabled=True
    ).select_related('attribute')[:10]
    
    context = {
        'object': obj,
        'systems': systems,
        'sensors_data': sensors_data,
        'stats': stats,
        'avg_temperature': round(avg_temperature, 1),
        'avg_humidity': round(avg_humidity, 1),
        'avg_power': round(avg_power, 1),
        'alerts': alerts,
        'floor_plan_url': None,  # TODO: добавить floor_plan в модель
    }
    
    return render(request, 'data/object_dashboard.html', context)


@login_required
def sensor_history(request, sensor_id):
    """История показаний датчика для графика"""
    # FIXED: Phase 4.1 использует company вместо устаревшего user
    if request.user.role == 'superadmin':
        attribute = get_object_or_404(Atributes, id=sensor_id)
    else:
        attribute = get_object_or_404(Atributes, id=sensor_id, sys__obj__company=request.user.company)
    
    # Период из параметров (по умолчанию 24 часа)
    hours = int(request.GET.get('hours', 24))
    now = timezone.now()
    start_time = now - timedelta(hours=hours)
    
    # Получаем данные
    data_points = Data.objects.filter(
        name=attribute,
        date__gte=start_time
    ).order_by('date').values('date', 'value')
    
    # Форматируем для Chart.js
    labels = [d['date'].strftime('%H:%M') for d in data_points]
    values = [float(d['value']) for d in data_points]
    
    return JsonResponse({
        'labels': labels,
        'values': values,
        'sensor_name': attribute.name,
        'unit': attribute.uom or '',
    })


@login_required
def realtime_data(request, object_id):
    """Реалтайм данные для обновления дашборда"""
    # FIXED: Phase 4.1 использует company вместо устаревшего user
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    # Получаем последние данные всех датчиков
    sensors = []
    for system in obj.system_set.all():
        for attr in system.atributes_set.all():
            latest = Data.objects.filter(name=attr).order_by('-date').first()
            if latest:
                sensors.append({
                    'id': attr.id,
                    'name': attr.name,
                    'value': float(latest.value),
                    'unit': attr.uom or '',
                    'timestamp': latest.date.isoformat(),
                })
    
    # Обновлённая статистика
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    avg_temp = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='температур',
        date__gte=last_hour
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    avg_hum = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='влажн',
        date__gte=last_hour
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    avg_pow = Data.objects.filter(
        name__sys__obj=obj,
        name__name__icontains='мощн',
        date__gte=last_hour
    ).aggregate(Avg('value'))['value__avg'] or 0
    
    # FIXED: AlertRule.company вместо несуществующего sys__obj
    return JsonResponse({
        'sensors': sensors,
        'stats': {
            'temperature': round(avg_temp, 1),
            'humidity': round(avg_hum, 1),
            'power': round(avg_pow, 1),
        },
        'alerts_count': AlertRule.objects.filter(company=obj.company, enabled=True).count(),
    })
