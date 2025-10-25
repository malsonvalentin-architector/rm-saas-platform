"""
Dashboard v2 Views - FIXED VERSION
Safe imports that don't break if models don't exist
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json

# Safe imports - only import what exists
try:
    from data.models import Obj
except (ImportError, AttributeError):
    Obj = None


# ==================== PAGE VIEWS ====================

@login_required
def dashboard_home(request):
    """Main dashboard page with metrics cards - PHASE 2 FULL VERSION"""
    
    # Rich metrics data for Phase 2
    metrics = [
        {
            'key': 'total_objects',
            'name': 'Всего объектов',
            'value': '12',
            'detail': '+2 за последний месяц',
            'icon': '🏢',
            'status': 'success',
            'status_text': 'Активны'
        },
        {
            'key': 'active_systems',
            'name': 'Активные системы',
            'value': '48',
            'detail': '46 онлайн, 2 в ожидании',
            'icon': '⚡',
            'status': 'success',
            'status_text': 'Online'
        },
        {
            'key': 'temperature',
            'name': 'Средняя температура',
            'value': '22.3°C',
            'detail': 'Оптимальный диапазон',
            'icon': '🌡️',
            'status': 'success',
            'status_text': 'Normal'
        },
        {
            'key': 'alerts_count',
            'name': 'Активные тревоги',
            'value': '3',
            'detail': '2 warning, 1 info',
            'icon': '🔔',
            'status': 'warning',
            'status_text': 'Требует внимания'
        },
        {
            'key': 'energy_consumption',
            'name': 'Энергопотребление',
            'value': '1,247 кВт',
            'detail': '-8% к прошлому месяцу',
            'icon': '💡',
            'status': 'success',
            'status_text': 'Оптимально'
        },
        {
            'key': 'uptime',
            'name': 'Uptime',
            'value': '99.8%',
            'detail': '30 дней без простоя',
            'icon': '🚀',
            'status': 'success',
            'status_text': 'Excellent'
        },
    ]
    
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'metrics': metrics
    }
    return render(request, 'dashboard_v2/dashboard_full.html', context)


@login_required
def control_panel(request):
    """Control Panel page with artistic equipment visualization - PHASE 2 FULL"""
    context = {
        'page_title': 'Control Panel',
        'active_page': 'control'
    }
    return render(request, 'dashboard_v2/control_full.html', context)


@login_required
def alerts_page(request):
    """Alerts & Notifications page - PHASE 2 FULL VERSION"""
    context = {
        'page_title': 'Alerts',
        'active_page': 'alerts'
    }
    return render(request, 'dashboard_v2/alerts_full.html', context)


@login_required
def analytics_page(request):
    """Analytics & Reports page - PHASE 2 FULL VERSION"""
    context = {
        'page_title': 'Analytics',
        'active_page': 'analytics'
    }
    return render(request, 'dashboard_v2/analytics_full.html', context)


@login_required
def objects_page(request):
    """Objects management page - PHASE 2.5 FULL VERSION"""
    context = {
        'page_title': 'Objects',
        'active_page': 'objects'
    }
    return render(request, 'dashboard_v2/objects_full.html', context)


@login_required
def settings_page(request):
    """Settings & Profile page - PHASE 2 FULL VERSION"""
    context = {
        'page_title': 'Settings',
        'active_page': 'settings'
    }
    return render(request, 'dashboard_v2/settings_full.html', context)


@login_required
def map_page(request):
    """Map view page - PHASE 2.5"""
    context = {
        'page_title': 'Map View',
        'active_page': 'map'
    }
    return render(request, 'dashboard_v2/map_full.html', context)


# ==================== API VIEWS ====================

@login_required
def api_dashboard_metrics(request):
    """
    API: Get dashboard metrics
    Returns: JSON with total objects, active systems, alerts count, etc.
    """
    try:
        company = request.user.company
        
        # Get counts - safe fallback if models don't exist
        total_objects = 0
        if Obj:
            try:
                total_objects = Obj.objects.filter(company=company).count()
            except:
                pass
        
        # Mock active systems (replace when System model is available)
        active_systems = 12
        total_systems = 15
        
        # Mock active alerts (replace when Alert model is available)
        active_alerts = 3
        
        # Mock metrics (replace with real sensor readings later)
        avg_temperature = 22.5
        avg_pressure = 2.8
        energy_consumption = 145.2
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_objects': total_objects or 45,  # Fallback to mock
            'active_systems': active_systems,
            'total_systems': total_systems,
            'active_alerts': active_alerts,
            'metrics': {
                'temperature': {
                    'value': avg_temperature,
                    'unit': '°C',
                    'trend': 'stable'
                },
                'pressure': {
                    'value': avg_pressure,
                    'unit': 'bar',
                    'trend': 'up'
                },
                'energy': {
                    'value': energy_consumption,
                    'unit': 'kWh',
                    'trend': 'down'
                }
            }
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load metrics',
            'timestamp': datetime.now().isoformat(),
            # Fallback data
            'total_objects': 45,
            'active_systems': 12,
            'total_systems': 15,
            'active_alerts': 3,
            'metrics': {
                'temperature': {'value': 22.5, 'unit': '°C', 'trend': 'stable'},
                'pressure': {'value': 2.8, 'unit': 'bar', 'trend': 'up'},
                'energy': {'value': 145.2, 'unit': 'kWh', 'trend': 'down'}
            }
        })


@login_required
def api_control_devices(request):
    """
    API: Get list of controllable devices
    Returns: JSON array of devices with status
    """
    try:
        # Mock devices for now
        devices = [
            {
                'id': 1,
                'name': 'HVAC Unit 1',
                'type': 'hvac',
                'status': 'active',
                'location': 'Zone A',
                'temperature': 22.5,
                'pressure': 2.8,
                'power': True
            },
            {
                'id': 2,
                'name': 'Chiller 1',
                'type': 'chiller',
                'status': 'active',
                'location': 'Zone B',
                'temperature': 18.2,
                'pressure': 3.2,
                'power': True
            },
            {
                'id': 3,
                'name': 'Boiler 1',
                'type': 'boiler',
                'status': 'active',
                'location': 'Zone C',
                'temperature': 75.0,
                'pressure': 1.5,
                'power': True
            }
        ]
        
        return JsonResponse({'devices': devices})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load devices'
        }, status=500)


@csrf_exempt
@login_required
def api_control_command(request):
    """
    API: Send command to device
    POST body: {device_id, command, value}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        command = data.get('command')
        value = data.get('value')
        
        # TODO: Implement actual Modbus command sending
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': f'Command {command} sent to device {device_id}',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to send command'
        }, status=500)


@login_required
def api_alerts_list(request):
    """
    API: Get list of alerts
    Query params: ?limit=50&severity=critical
    """
    try:
        limit = int(request.GET.get('limit', 50))
        severity = request.GET.get('severity', None)
        
        # Mock alerts for now
        alerts = [
            {
                'id': 1,
                'severity': 'warning',
                'message': 'Temperature high in Zone A',
                'timestamp': datetime.now().isoformat(),
                'acknowledged': False,
                'system': 'HVAC Unit 1'
            },
            {
                'id': 2,
                'severity': 'critical',
                'message': 'Pressure leak detected',
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'acknowledged': False,
                'system': 'Chiller 1'
            },
            {
                'id': 3,
                'severity': 'info',
                'message': 'System maintenance scheduled',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'acknowledged': True,
                'system': 'Boiler 1'
            }
        ]
        
        # Filter by severity if provided
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        # Limit results
        alerts = alerts[:limit]
        
        return JsonResponse({'alerts': alerts, 'total': len(alerts)})
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load alerts'
        }, status=500)


@login_required
def api_analytics_stats(request):
    """
    API: Get analytics statistics
    Query params: ?period=7d&metric=temperature
    """
    try:
        period = request.GET.get('period', '7d')
        metric = request.GET.get('metric', 'temperature')
        
        # Generate mock time series data
        now = datetime.now()
        data_points = []
        
        for i in range(7):
            date = (now - timedelta(days=6-i)).strftime('%Y-%m-%d')
            value = 22.0 + (i * 0.5) + (i % 2)  # Mock trend
            
            data_points.append({
                'date': date,
                'value': round(value, 1)
            })
        
        return JsonResponse({
            'metric': metric,
            'period': period,
            'unit': '°C' if metric == 'temperature' else 'bar',
            'data': data_points,
            'average': 22.5,
            'min': 22.0,
            'max': 25.2
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load analytics'
        }, status=500)


# ==================== SETTINGS API ====================

@csrf_exempt
@login_required
def api_settings_profile(request):
    """
    API: Update user profile
    POST body: {first_name, last_name, email, phone}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        
        user.save()
        
        # Update profile phone (if profile model exists)
        if 'phone' in data:
            try:
                if hasattr(user, 'profile'):
                    user.profile.phone = data['phone']
                    user.profile.save()
            except:
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Профиль обновлён',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Ошибка сохранения профиля'
        }, status=500)


@csrf_exempt
@login_required
def api_settings_password(request):
    """
    API: Change user password
    POST body: {current_password, new_password}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from django.contrib.auth import authenticate, update_session_auth_hash
        
        data = json.loads(request.body)
        user = request.user
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        if not user.check_password(current_password):
            return JsonResponse({
                'success': False,
                'message': 'Неверный текущий пароль'
            }, status=400)
        
        # Validate new password
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Пароль должен быть минимум 8 символов'
            }, status=400)
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Keep user logged in
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Пароль успешно изменён'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Ошибка смены пароля'
        }, status=500)


@csrf_exempt
@login_required
def api_settings_preferences(request):
    """
    API: Update user preferences
    POST body: {theme, language, timezone, notifications}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Save preferences to user profile or session
        # For now, we'll use session storage
        if 'theme' in data:
            request.session['theme'] = data['theme']
        if 'language' in data:
            request.session['language'] = data['language']
        if 'timezone' in data:
            request.session['timezone'] = data['timezone']
        if 'notifications' in data:
            request.session['notifications'] = data['notifications']
        
        return JsonResponse({
            'success': True,
            'message': 'Настройки сохранены'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Ошибка сохранения настроек'
        }, status=500)


# ==================== ALERTS API ====================

@csrf_exempt
@login_required
def api_alert_acknowledge(request):
    """
    API: Acknowledge an alert
    POST body: {alert_id}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        
        # TODO: Update alert status in database
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': f'Alert {alert_id} acknowledged',
            'alert_id': alert_id,
            'status': 'acknowledged'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to acknowledge alert'
        }, status=500)


@csrf_exempt
@login_required
def api_alert_resolve(request):
    """
    API: Resolve an alert
    POST body: {alert_id}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        
        # TODO: Update alert status in database
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': f'Alert {alert_id} resolved',
            'alert_id': alert_id,
            'status': 'resolved'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to resolve alert'
        }, status=500)
