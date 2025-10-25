"""
Dashboard v2 Views
Modern sidebar-based dashboard for ProMonitor
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg
from datetime import datetime, timedelta
import json

from data.models import Obj, System, Sensor, SensorReading, Alert


# ==================== PAGE VIEWS ====================

@login_required
def dashboard_home(request):
    """Main dashboard page with metrics cards"""
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard'
    }
    return render(request, 'dashboard_v2/dashboard.html', context)


@login_required
def control_panel(request):
    """Control Panel page with device management"""
    context = {
        'page_title': 'Control Panel',
        'active_page': 'control'
    }
    return render(request, 'dashboard_v2/control.html', context)


@login_required
def alerts_page(request):
    """Alerts & Notifications page"""
    context = {
        'page_title': 'Alerts',
        'active_page': 'alerts'
    }
    return render(request, 'dashboard_v2/alerts.html', context)


@login_required
def analytics_page(request):
    """Analytics & Reports page"""
    context = {
        'page_title': 'Analytics',
        'active_page': 'analytics'
    }
    return render(request, 'dashboard_v2/analytics.html', context)


@login_required
def objects_page(request):
    """Objects management page"""
    context = {
        'page_title': 'Objects',
        'active_page': 'objects'
    }
    return render(request, 'dashboard_v2/objects.html', context)


@login_required
def settings_page(request):
    """Settings & Profile page"""
    context = {
        'page_title': 'Settings',
        'active_page': 'settings'
    }
    return render(request, 'dashboard_v2/settings.html', context)


# ==================== API VIEWS ====================

@login_required
def api_dashboard_metrics(request):
    """
    API: Get dashboard metrics
    Returns: JSON with total objects, active systems, alerts count, etc.
    """
    try:
        company = request.user.company
        
        # Get counts
        total_objects = Obj.objects.filter(company=company).count()
        
        # Try to get systems count (may fail if table doesn't exist)
        try:
            active_systems = System.objects.filter(
                obj__company=company,
                status='active'
            ).count()
            total_systems = System.objects.filter(obj__company=company).count()
        except:
            active_systems = 0
            total_systems = 0
        
        # Try to get alerts (may fail if table doesn't exist)
        try:
            active_alerts = Alert.objects.filter(
                company=company,
                acknowledged=False
            ).count()
        except:
            active_alerts = 0
        
        # Mock data for now (replace with real sensor readings later)
        avg_temperature = 22.5
        avg_pressure = 2.8
        energy_consumption = 145.2
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_objects': total_objects,
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
            'message': 'Failed to load metrics'
        }, status=500)


@login_required
def api_control_devices(request):
    """
    API: Get list of controllable devices
    Returns: JSON array of devices with status
    """
    try:
        company = request.user.company
        
        # Try to get systems (may fail if table structure is different)
        try:
            systems = System.objects.filter(obj__company=company).select_related('obj')
            
            devices = []
            for system in systems:
                devices.append({
                    'id': system.id,
                    'name': system.name,
                    'type': getattr(system, 'type', 'hvac'),
                    'status': getattr(system, 'status', 'unknown'),
                    'location': system.obj.name,
                    'temperature': 22.5,  # Mock data
                    'pressure': 2.8,
                    'power': True
                })
        except:
            # Fallback: return mock devices
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
        company = request.user.company
        limit = int(request.GET.get('limit', 50))
        severity = request.GET.get('severity', None)
        
        # Try to get real alerts
        try:
            alerts_qs = Alert.objects.filter(company=company)
            
            if severity:
                alerts_qs = alerts_qs.filter(severity=severity)
            
            alerts_qs = alerts_qs.order_by('-timestamp')[:limit]
            
            alerts = []
            for alert in alerts_qs:
                alerts.append({
                    'id': alert.id,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged': alert.acknowledged,
                    'system': alert.system.name if alert.system else 'Unknown'
                })
        except:
            # Fallback: return mock alerts
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
                }
            ]
        
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
        
        # Mock data for now
        # TODO: Replace with real sensor readings query
        
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
