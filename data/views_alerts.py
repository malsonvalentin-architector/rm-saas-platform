"""
Views для системы тревог (Alerts System)
Phase 4.3 - ProMonitor.kz
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta
from .models import AlertRule, AlertEvent, AlertComment


@login_required
def alerts_list(request):
    """
    Главная страница тревог - показывает активные и недавние тревоги
    Фильтры: статус, серьёзность, объект, система
    """
    company = request.user.company
    
    # Получаем параметры фильтров
    status_filter = request.GET.get('status', 'active')  # active, acknowledged, resolved, snoozed, all
    severity_filter = request.GET.get('severity', '')
    object_filter = request.GET.get('object_id', '')
    system_filter = request.GET.get('system_id', '')
    search_query = request.GET.get('search', '')
    
    # Базовый queryset - все тревоги компании
    alerts = AlertEvent.objects.filter(
        rule__attribute__sys__obj__company=company
    ).select_related(
        'rule',
        'rule__attribute',
        'rule__attribute__sys',
        'rule__attribute__sys__obj',
        'acknowledged_by',
        'resolved_by'
    ).order_by('-triggered_at')
    
    # Фильтр по статусу
    if status_filter == 'active':
        alerts = alerts.filter(status='active')
    elif status_filter == 'acknowledged':
        alerts = alerts.filter(status='acknowledged')
    elif status_filter == 'resolved':
        alerts = alerts.filter(status='resolved')
    elif status_filter == 'snoozed':
        alerts = alerts.filter(status='snoozed', snoozed_until__gt=timezone.now())
    # 'all' - не фильтруем
    
    # Фильтр по серьёзности
    if severity_filter:
        alerts = alerts.filter(rule__severity=severity_filter)
    
    # Фильтр по объекту
    if object_filter:
        alerts = alerts.filter(rule__attribute__sys__obj_id=object_filter)
    
    # Фильтр по системе
    if system_filter:
        alerts = alerts.filter(rule__attribute__sys_id=system_filter)
    
    # Поиск по названию правила или описанию
    if search_query:
        alerts = alerts.filter(
            Q(rule__name__icontains=search_query) |
            Q(rule__description__icontains=search_query) |
            Q(rule__attribute__name__icontains=search_query)
        )
    
    # Статистика по тревогам
    total_alerts = alerts.count()
    active_count = AlertEvent.objects.filter(
        rule__attribute__sys__obj__company=company,
        status='active'
    ).count()
    acknowledged_count = AlertEvent.objects.filter(
        rule__attribute__sys__obj__company=company,
        status='acknowledged'
    ).count()
    resolved_today = AlertEvent.objects.filter(
        rule__attribute__sys__obj__company=company,
        status='resolved',
        resolved_at__date=timezone.now().date()
    ).count()
    
    # Средняя длительность разрешения тревог за последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)
    recent_resolved = AlertEvent.objects.filter(
        rule__attribute__sys__obj__company=company,
        status='resolved',
        resolved_at__gte=week_ago
    )
    
    avg_resolution_seconds = 0
    if recent_resolved.exists():
        durations = []
        for alert in recent_resolved:
            if alert.resolved_at and alert.triggered_at:
                duration = (alert.resolved_at - alert.triggered_at).total_seconds()
                durations.append(duration)
        if durations:
            avg_resolution_seconds = sum(durations) / len(durations)
    
    avg_resolution_minutes = int(avg_resolution_seconds / 60)
    
    # Критические тревоги (для выделения)
    critical_alerts = alerts.filter(rule__severity='critical', status='active')[:5]
    
    # Список объектов и систем для фильтров
    from .models import Obj, System
    objects_list = Obj.objects.filter(company=company).order_by('obj')
    systems_list = System.objects.filter(obj__company=company).order_by('name')
    
    # Ограничиваем количество тревог на странице
    alerts = alerts[:100]  # Показываем последние 100 тревог
    
    context = {
        'alerts': alerts,
        'critical_alerts': critical_alerts,
        'total_alerts': total_alerts,
        'active_count': active_count,
        'acknowledged_count': acknowledged_count,
        'resolved_today': resolved_today,
        'avg_resolution_minutes': avg_resolution_minutes,
        'objects_list': objects_list,
        'systems_list': systems_list,
        # Текущие фильтры для сохранения состояния
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'object_filter': object_filter,
        'system_filter': system_filter,
        'search_query': search_query,
    }
    
    return render(request, 'data/alerts_list.html', context)


@login_required
def alert_acknowledge(request, alert_id):
    """
    Подтверждение тревоги (acknowledge)
    """
    alert = get_object_or_404(AlertEvent, id=alert_id)
    
    # Проверка прав доступа
    if alert.rule.attribute.sys.obj.company != request.user.company:
        messages.error(request, "У вас нет доступа к этой тревоге")
        return redirect('data:alerts_list')
    
    if alert.status == 'active':
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        # Добавляем автоматический комментарий
        AlertComment.objects.create(
            event=alert,
            user=request.user,
            text=f"Тревога подтверждена пользователем {request.user.get_full_name() or request.user.username}"
        )
        
        messages.success(request, f"✅ Тревога '{alert.rule.name}' подтверждена")
    else:
        messages.warning(request, "Тревога уже обработана")
    
    # Возвращаемся на страницу тревог
    return redirect('data:alerts_list')


@login_required
def alert_resolve(request, alert_id):
    """
    Отметить тревогу как решённую (resolve)
    """
    alert = get_object_or_404(AlertEvent, id=alert_id)
    
    # Проверка прав доступа
    if alert.rule.attribute.sys.obj.company != request.user.company:
        messages.error(request, "У вас нет доступа к этой тревоге")
        return redirect('data:alerts_list')
    
    if alert.status in ['active', 'acknowledged', 'snoozed']:
        alert.status = 'resolved'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        
        # Добавляем автоматический комментарий
        duration = alert.get_duration()
        AlertComment.objects.create(
            event=alert,
            user=request.user,
            text=f"Тревога решена пользователем {request.user.get_full_name() or request.user.username}. Длительность: {duration}"
        )
        
        messages.success(request, f"✅ Тревога '{alert.rule.name}' отмечена как решённая")
    else:
        messages.warning(request, "Тревога уже решена")
    
    return redirect('data:alerts_list')


@login_required
def alert_snooze(request, alert_id):
    """
    Отложить тревогу на заданное время (snooze)
    """
    alert = get_object_or_404(AlertEvent, id=alert_id)
    
    # Проверка прав доступа
    if alert.rule.attribute.sys.obj.company != request.user.company:
        messages.error(request, "У вас нет доступа к этой тревоге")
        return redirect('data:alerts_list')
    
    if request.method == 'POST':
        snooze_minutes = int(request.POST.get('snooze_minutes', 60))
        
        if alert.status in ['active', 'acknowledged']:
            alert.status = 'snoozed'
            alert.snooze_until = timezone.now() + timedelta(minutes=snooze_minutes)
            alert.snoozed_by = request.user
            alert.save()
            
            # Добавляем автоматический комментарий
            AlertComment.objects.create(
                event=alert,
                user=request.user,
                text=f"Тревога отложена на {snooze_minutes} минут пользователем {request.user.get_full_name() or request.user.username}"
            )
            
            messages.success(request, f"⏰ Тревога '{alert.rule.name}' отложена на {snooze_minutes} минут")
        else:
            messages.warning(request, "Невозможно отложить эту тревогу")
    
    return redirect('data:alerts_list')


@login_required
def alert_add_comment(request, alert_id):
    """
    Добавить комментарий к тревоге
    """
    alert = get_object_or_404(AlertEvent, id=alert_id)
    
    # Проверка прав доступа
    if alert.rule.attribute.sys.obj.company != request.user.company:
        messages.error(request, "У вас нет доступа к этой тревоге")
        return redirect('data:alerts_list')
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            AlertComment.objects.create(
                event=alert,
                user=request.user,
                text=comment_text
            )
            messages.success(request, "💬 Комментарий добавлен")
        else:
            messages.warning(request, "Комментарий не может быть пустым")
    
    return redirect('data:alerts_list')


@login_required
def alert_detail(request, alert_id):
    """
    Детальная информация о тревоге (используется для AJAX или отдельной страницы)
    """
    alert = get_object_or_404(AlertEvent, id=alert_id)
    
    # Проверка прав доступа
    if alert.rule.attribute.sys.obj.company != request.user.company:
        messages.error(request, "У вас нет доступа к этой тревоге")
        return redirect('data:alerts_list')
    
    # Получаем все комментарии к тревоге
    comments = alert.comments.all().select_related('user').order_by('-created_at')
    
    # История значений датчика вокруг времени срабатывания
    from .models import Data
    triggered_time = alert.triggered_at
    history_start = triggered_time - timedelta(hours=1)
    history_end = triggered_time + timedelta(hours=1)
    
    sensor_history = Data.objects.filter(
        atribute=alert.rule.attribute,
        timestamp__gte=history_start,
        timestamp__lte=history_end
    ).order_by('timestamp')[:50]
    
    context = {
        'alert': alert,
        'comments': comments,
        'sensor_history': sensor_history,
    }
    
    return render(request, 'data/alert_detail.html', context)
