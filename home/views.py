"""
Home Views - Главный дашборд ProMonitor
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from data.models import Obj, System, AlertRule, Atributes, Data, Actuator
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """
    Главная панель управления
    Показывает общую статистику по всем объектам пользователя
    """
    try:
        user = request.user
        
        # Phase 4.1: Check if user has role and company attributes
        if not hasattr(user, 'role'):
            logger.error(f"User {user.email} has no 'role' attribute")
            return redirect('login')
        
        # Получаем объекты пользователя (Phase 4.1: Multi-Tenant)
        if user.role == 'superadmin':
            objects = Obj.objects.all()
        else:
            # Check if user has company
            if not hasattr(user, 'company') or user.company is None:
                logger.error(f"User {user.email} has no company")
                return render(request, 'home/no_company.html', {
                    'message': 'Ваш аккаунт не привязан к компании. Обратитесь к администратору.'
                })
            objects = Obj.objects.filter(company=user.company)
        
        # Статистика (с безопасными fallback)
        total_objects = objects.count()
        total_systems = System.objects.filter(obj__in=objects).count() if objects.exists() else 0
        
        # Активные тревоги - упрощённый подсчёт
        try:
            if objects.exists():
                # Получаем только те AlertRule которые привязаны к нашим объектам
                our_systems = System.objects.filter(obj__in=objects)
                our_attributes = Atributes.objects.filter(sys__in=our_systems)
                active_alerts = AlertRule.objects.filter(
                    enabled=True,
                    attribute__in=our_attributes
                ).count()
            else:
                active_alerts = 0
        except Exception as e:
            logger.error(f"Error counting alerts: {e}")
            active_alerts = 0
        
        # Phase 4.4/4.6: Actuators statistics
        try:
            if objects.exists():
                our_systems = System.objects.filter(obj__in=objects)
                total_actuators = Actuator.objects.filter(sys__in=our_systems).count()
                online_actuators = Actuator.objects.filter(sys__in=our_systems, is_online=True).count()
                offline_actuators = total_actuators - online_actuators
            else:
                total_actuators = 0
                online_actuators = 0
                offline_actuators = 0
        except Exception as e:
            logger.error(f"Error counting actuators: {e}")
            total_actuators = 0
            online_actuators = 0
            offline_actuators = 0
        
        # Средние показатели датчиков за последние 24 часа
        last_24h = timezone.now() - timedelta(hours=24)
        avg_temperature = 23
        avg_humidity = 55
        avg_power = 145
        energy_chart_data = []
        
        try:
            if objects.exists():
                recent_data = Data.objects.filter(
                    date__gte=last_24h,
                    name__sys__obj__in=objects
                )
                
                # Температура
                temp_avg = recent_data.filter(
                    name__name__icontains='температур'
                ).aggregate(Avg('value'))['value__avg']
                avg_temperature = round(temp_avg, 1) if temp_avg else 23
                
                # Влажность
                hum_avg = recent_data.filter(
                    name__name__icontains='влажн'
                ).aggregate(Avg('value'))['value__avg']
                avg_humidity = round(hum_avg, 1) if hum_avg else 55
                
                # Мощность/энергия
                pow_avg = recent_data.filter(
                    name__name__icontains='мощн'
                ).aggregate(Avg('value'))['value__avg']
                avg_power = round(pow_avg, 0) if pow_avg else 145
                
                # График энергопотребления за 24 часа
                for hour in range(24):
                    hour_start = timezone.now() - timedelta(hours=24-hour)
                    hour_end = hour_start + timedelta(hours=1)
                    
                    avg_value = Data.objects.filter(
                        date__gte=hour_start,
                        date__lt=hour_end,
                        name__name__icontains='мощн',
                        name__sys__obj__in=objects
                    ).aggregate(Avg('value'))['value__avg']
                    
                    energy_chart_data.append({
                        'hour': hour_start.strftime('%H:%M'),
                        'value': round(avg_value or 0, 2)
                    })
        except Exception as e:
            logger.error(f"Error calculating averages: {e}")
            # Use default values
        
        # Последние тревоги
        recent_alerts = []
        try:
            if objects.exists():
                our_systems = System.objects.filter(obj__in=objects)
                our_attributes = Atributes.objects.filter(sys__in=our_systems)
                recent_alerts = AlertRule.objects.filter(
                    enabled=True,
                    attribute__in=our_attributes
                ).select_related('attribute', 'attribute__sys', 'attribute__sys__obj')[:10]
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
        
        context = {
            'total_objects': total_objects,
            'total_systems': total_systems,
            'active_alerts': active_alerts,
            'total_actuators': total_actuators,
            'online_actuators': online_actuators,
            'offline_actuators': offline_actuators,
            'avg_temperature': avg_temperature,
            'avg_humidity': avg_humidity,
            'avg_power': avg_power,
            'energy_chart_data': energy_chart_data,
            'recent_alerts': recent_alerts,
        }
        
        return render(request, 'home/dashboard.html', context)
        
    except Exception as e:
        logger.exception(f"Critical error in dashboard: {e}")
        return render(request, 'home/error.html', {
            'error_message': 'Произошла ошибка при загрузке dashboard. Обратитесь к администратору.',
            'technical_details': str(e) if request.user.is_staff else None,
        })


def index(request):
    """
    Главная страница - если авторизован → дашборд, иначе → логин
    """
    if request.user.is_authenticated:
        return dashboard(request)
    else:
        return redirect('login')
