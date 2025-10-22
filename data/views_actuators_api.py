"""
API Views для Real-Time данных актуаторов
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncHour, TruncMinute

from .models import Actuator, ActuatorCommand


@login_required
@require_http_methods(["GET"])
def actuators_live_stats(request):
    """
    Возвращает live статистику для dashboard
    """
    # Статистика устройств
    total = Actuator.objects.count()
    online = Actuator.objects.filter(is_online=True).count()
    active = Actuator.objects.filter(is_active=True).count()
    
    # Команды за последние 24 часа
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    commands_24h = ActuatorCommand.objects.filter(
        executed_at__gte=last_24h
    ).count()
    
    # Последние 5 команд
    recent_commands = ActuatorCommand.objects.select_related(
        'actuator', 'actuator__sys', 'actuator__sys__obj'
    ).order_by('-executed_at')[:5]
    
    recent_commands_data = []
    for cmd in recent_commands:
        # Безопасное получение названия объекта
        object_name = 'N/A'
        try:
            if cmd.actuator and cmd.actuator.sys and cmd.actuator.sys.obj:
                object_name = cmd.actuator.sys.obj.obj
        except AttributeError:
            pass
        
        recent_commands_data.append({
            'id': cmd.id,
            'actuator_name': cmd.actuator.name if cmd.actuator else 'N/A',
            'object_name': object_name,
            'value': float(cmd.command_value),
            'timestamp': cmd.executed_at.isoformat(),
            'success': cmd.status == 'success',
        })
    
    return JsonResponse({
        'stats': {
            'total': total,
            'online': online,
            'active': active,
            'commands_24h': commands_24h,
        },
        'recent_commands': recent_commands_data,
        'timestamp': now.isoformat(),
    })


@login_required
@require_http_methods(["GET"])
def actuators_commands_timeline(request):
    """
    Возвращает timeline команд для графика
    Группирует по часам за последние 24 часа
    """
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    # Группируем команды по часам
    commands_by_hour = ActuatorCommand.objects.filter(
        executed_at__gte=last_24h
    ).annotate(
        hour=TruncHour('executed_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    # Формируем данные для графика
    labels = []
    data = []
    
    for item in commands_by_hour:
        labels.append(item['hour'].strftime('%H:%M'))
        data.append(item['count'])
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'timestamp': now.isoformat(),
    })


@login_required
@require_http_methods(["GET"])
def actuators_activity_chart(request):
    """
    Возвращает данные активности устройств за последний час
    Группирует по 10-минутным интервалам
    """
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    # Упрощённый вариант без raw SQL - группируем по минутам
    commands_by_minute = ActuatorCommand.objects.filter(
        executed_at__gte=last_hour
    ).annotate(
        minute=TruncMinute('executed_at')
    ).values('minute').annotate(
        count=Count('id')
    ).order_by('minute')
    
    labels = []
    data = []
    
    # Группируем по 10 минут в Python
    current_interval = None
    interval_count = 0
    
    for item in commands_by_minute:
        minute_time = item['minute']
        # Округляем до 10 минут
        interval = minute_time.replace(minute=(minute_time.minute // 10) * 10, second=0, microsecond=0)
        
        if current_interval != interval:
            if current_interval is not None:
                labels.append(current_interval.strftime('%H:%M'))
                data.append(interval_count)
            current_interval = interval
            interval_count = 0
        
        interval_count += item['count']
    
    # Добавляем последний интервал
    if current_interval is not None:
        labels.append(current_interval.strftime('%H:%M'))
        data.append(interval_count)
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'timestamp': now.isoformat(),
    })


@login_required
@require_http_methods(["GET"])
def actuators_by_type(request):
    """
    Возвращает количество устройств по типам для pie chart
    """
    devices_by_type = Actuator.objects.values(
        'actuator_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Маппинг типов на иконки и названия
    type_labels = {
        'valve': '🚰 Клапаны',
        'relay': '⚡ Реле',
        'motor': '⚙️ Моторы',
        'switch': '💡 Выключатели',
        'dimmer': '🔆 Диммеры',
        'pump': '💧 Насосы',
        'fan': '🌀 Вентиляторы',
        'heater': '🔥 Нагреватели',
        'cooler': '❄️ Охладители',
    }
    
    labels = []
    data = []
    
    for item in devices_by_type:
        device_type = item['actuator_type']
        label = type_labels.get(device_type, device_type)
        labels.append(label)
        data.append(item['count'])
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'timestamp': timezone.now().isoformat(),
    })
