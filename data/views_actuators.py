"""
VIEWS ДЛЯ УПРАВЛЕНИЯ УСТРОЙСТВАМИ (Phase 4.4 MVP)

Философия Steve Jobs:
- Простота и элегантность
- Фокус на пользовательском опыте
- Начинаем с базового, потом расширяем

Основные функции:
1. actuators_list - список всех устройств
2. actuator_control - отправка команды управления
3. actuator_history - история команд устройства
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import Actuator, ActuatorCommand, System, Obj


@login_required
def actuators_list(request):
    """
    Главная страница управления устройствами
    
    Показывает:
    - Карточки со статистикой
    - Список всех устройств с фильтрами
    - Быстрые кнопки управления
    """
    
    company = request.user.company
    
    # Получаем все актуаторы компании
    actuators = Actuator.objects.filter(
        sys__obj__company=company
    ).select_related(
        'sys', 'sys__obj'
    ).order_by('sys__obj__obj', 'sys__name', 'name')
    
    # Фильтры
    actuator_type = request.GET.get('type', '')
    object_id = request.GET.get('object', '')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if actuator_type:
        actuators = actuators.filter(actuator_type=actuator_type)
    
    if object_id:
        actuators = actuators.filter(sys__obj__id=object_id)
    
    if status_filter == 'active':
        actuators = actuators.filter(is_active=True)
    elif status_filter == 'inactive':
        actuators = actuators.filter(is_active=False)
    elif status_filter == 'online':
        actuators = actuators.filter(is_online=True)
    elif status_filter == 'offline':
        actuators = actuators.filter(is_online=False)
    
    if search:
        actuators = actuators.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(sys__name__icontains=search) |
            Q(sys__obj__obj__icontains=search)
        )
    
    # Статистика
    total_actuators = Actuator.objects.filter(sys__obj__company=company).count()
    online_actuators = Actuator.objects.filter(sys__obj__company=company, is_online=True).count()
    active_actuators = Actuator.objects.filter(sys__obj__company=company, is_active=True).count()
    
    # Команды за последние 24 часа
    commands_24h = ActuatorCommand.objects.filter(
        actuator__sys__obj__company=company,
        executed_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    
    # Объекты для фильтра
    objects = Obj.objects.filter(company=company).order_by('obj')
    
    # Типы устройств для фильтра
    actuator_types = Actuator.ACTUATOR_TYPES
    
    context = {
        'actuators': actuators,
        'total_actuators': total_actuators,
        'online_actuators': online_actuators,
        'active_actuators': active_actuators,
        'commands_24h': commands_24h,
        'objects': objects,
        'actuator_types': actuator_types,
        # Фильтры для сохранения состояния
        'current_type': actuator_type,
        'current_object': object_id,
        'current_status': status_filter,
        'search_query': search,
    }
    
    return render(request, 'data/actuators_list.html', context)


@login_required
def actuator_control(request, actuator_id):
    """
    Отправка команды управления устройством
    
    Параметры POST:
    - value: значение команды (float)
    - notes: примечания (optional)
    """
    
    if request.method != 'POST':
        messages.error(request, "Метод не разрешён")
        return redirect('actuators_list')
    
    company = request.user.company
    
    # Проверяем доступ к устройству
    actuator = get_object_or_404(
        Actuator.objects.filter(sys__obj__company=company),
        id=actuator_id
    )
    
    # Получаем значение команды
    try:
        value = float(request.POST.get('value', 0))
    except ValueError:
        messages.error(request, "Некорректное значение команды")
        return redirect('actuators_list')
    
    # Проверяем диапазон
    if not (actuator.min_value <= value <= actuator.max_value):
        messages.error(request, f"Значение должно быть от {actuator.min_value} до {actuator.max_value}")
        return redirect('actuators_list')
    
    # Получаем IP адрес
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        source_ip = x_forwarded_for.split(',')[0]
    else:
        source_ip = request.META.get('REMOTE_ADDR')
    
    # Создаём команду
    command = ActuatorCommand.objects.create(
        actuator=actuator,
        command_value=value,
        user=request.user,
        notes=request.POST.get('notes', ''),
        source_ip=source_ip,
        status='pending'
    )
    
    # TODO: Здесь будет реальная отправка команды через Modbus
    # Пока просто симулируем успех
    command.status = 'success'
    command.response_time_ms = 150  # Симуляция
    command.save()
    
    # Обновляем текущее значение актуатора
    actuator.current_value = value
    actuator.last_command_at = timezone.now()
    actuator.save()
    
    messages.success(request, f"✅ Команда выполнена: {actuator.name} = {actuator.get_display_value()}")
    
    # Возвращаем JSON для AJAX или редирект для обычного POST
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'actuator_id': actuator.id,
            'current_value': actuator.current_value,
            'display_value': actuator.get_display_value(),
            'command_id': command.id,
        })
    
    return redirect('actuators_list')


@login_required
def actuator_history(request, actuator_id):
    """
    История команд устройства
    """
    
    company = request.user.company
    
    # Проверяем доступ к устройству
    actuator = get_object_or_404(
        Actuator.objects.filter(sys__obj__company=company),
        id=actuator_id
    )
    
    # Получаем команды
    commands = ActuatorCommand.objects.filter(
        actuator=actuator
    ).select_related('user').order_by('-executed_at')[:100]  # Последние 100 команд
    
    # Статистика
    total_commands = ActuatorCommand.objects.filter(actuator=actuator).count()
    success_commands = ActuatorCommand.objects.filter(actuator=actuator, status='success').count()
    failed_commands = ActuatorCommand.objects.filter(actuator=actuator, status='failed').count()
    
    success_rate = (success_commands / total_commands * 100) if total_commands > 0 else 0
    
    context = {
        'actuator': actuator,
        'commands': commands,
        'total_commands': total_commands,
        'success_commands': success_commands,
        'failed_commands': failed_commands,
        'success_rate': success_rate,
    }
    
    return render(request, 'data/actuator_history.html', context)
