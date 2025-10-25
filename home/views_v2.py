"""
ProMonitor V2 - Enhanced Dashboard Views
Modern dashboard with honeycomb building visualization
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from django.contrib import messages
import json
from datetime import timedelta, datetime

from data.models import Obj as Building, System as SensorSystem, Atributes as Sensor, Data as SensorReading, AlertEvent as Alert, User_profile as UserProfile, ModbusConnection, ModbusRegisterMap
from .utils import get_building_status, calculate_sensor_health


@login_required
def dashboard_v2_standalone(request):
    """Standalone Dashboard V2 with embedded styles"""
    from django.shortcuts import render
    from data.models import Obj, Atributes, AlertEvent
    
    context = {
        'buildings_count': Obj.objects.count(),
        'sensors_count': Atributes.objects.count(),
        'alerts_count': AlertEvent.objects.filter(resolved=False).count() if hasattr(AlertEvent, 'resolved') else AlertEvent.objects.count(),
    }
    
    return render(request, 'dashboard/v2/dashboard_standalone.html', context)

def dashboard_v2(request):
    """
    Main dashboard v2 with honeycomb building visualization
    """
    # Get user profile for theme and dashboard preferences
    # request.user is already UserProfile (AUTH_USER_MODEL = 'data.User_profile')
    profile = request.user
    
    # Update preferences if needed
    if not hasattr(profile, 'theme') or profile.theme is None:
        profile.theme = 'dark'
    if not hasattr(profile, 'dashboard_version') or profile.dashboard_version is None:
        profile.dashboard_version = 'v2'
    profile.save()
    
    # Get company buildings (superadmin sees all)
    if request.user.role == 'superadmin':
        buildings = Building.objects.all().select_related('company')
        total_sensors = Sensor.objects.count()
        active_alerts = Alert.objects.filter(status='active').count()
    else:
        buildings = Building.objects.filter(company=request.user.company).select_related('company')
        total_sensors = Sensor.objects.filter(sys__obj__company=request.user.company).count()
        active_alerts = Alert.objects.filter(
            rule__attribute__sys__obj__company=request.user.company,
            status='active'
        ).count()
    
    # Calculate overview statistics
    total_buildings = buildings.count()
    
    # Building status counts
    building_statuses = {
        'healthy': 0,
        'warning': 0,
        'critical': 0,
        'offline': 0
    }
    
    # Prepare buildings data for honeycomb map
    honeycomb_buildings = []
    
    for building in buildings:
        # Get building sensor systems
        sensor_systems = SensorSystem.objects.filter(obj=building)
        # Get individual sensors (attributes) for this building
        sensors = Sensor.objects.filter(sys__obj=building).select_related('sys')
        sensor_count = sensors.count()
        
        # Calculate building status and metrics
        status = get_building_status(building)
        building_statuses[status] += 1
        
        # Get latest readings for temperature and humidity
        temp_reading = None
        humidity_reading = None
        
        if sensor_count > 0:
            # Get latest temperature reading
            temp_sensor = sensors.filter(name__icontains='temperature').first()
            if temp_sensor:
                temp_reading = SensorReading.objects.filter(
                    name=temp_sensor
                ).order_by('-date').first()
            
            # Get latest humidity reading
            humidity_sensor = sensors.filter(name__icontains='humidity').first()
            if humidity_sensor:
                humidity_reading = SensorReading.objects.filter(
                    name=humidity_sensor
                ).order_by('-date').first()
        
        # Get sensor details for sidebar
        sensor_details = []
        for sensor in sensors[:10]:  # Limit to first 10 sensors
            latest_reading = SensorReading.objects.filter(
                name=sensor
            ).order_by('-date').first()
            
            sensor_health = calculate_sensor_health(sensor)
            
            sensor_details.append({
                'name': sensor.name,
                'value': latest_reading.value if latest_reading else 'N/A',
                'unit': sensor.uom,
                'status': sensor_health,
                'last_update': latest_reading.date if latest_reading else None
            })
        
        # Build honeycomb data structure
        honeycomb_building = {
            'id': f'building-{building.id}',
            'name': building.obj,  # Field name in Obj model
            'status': status,
            'sensorCount': sensor_count,
            'temperature': temp_reading.value if temp_reading else None,
            'humidity': humidity_reading.value if humidity_reading else None,
            'icon': get_building_icon(building),
            'sensors': sensor_details,
            'location': {
                'lat': None,  # Obj model doesn't have lat/lng yet
                'lng': None
            }
        }
        
        honeycomb_buildings.append(honeycomb_building)
    
    # Recent alerts for timeline
    recent_alerts = Alert.objects.filter(
        rule__attribute__sys__obj__company=request.user.company
    ).select_related('rule', 'rule__attribute', 'rule__attribute__sys__obj').order_by('-triggered_at')[:10]
    
    # System health metrics
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    
    # Sensor readings in last hour vs 24h (activity indicator)
    readings_last_hour = SensorReading.objects.filter(
        name__sys__obj__company=request.user.company,
        date__gte=last_hour
    ).count()
    
    readings_last_24h = SensorReading.objects.filter(
        name__sys__obj__company=request.user.company,
        date__gte=last_24h
    ).count()
    
    # Calculate system uptime percentage
    total_expected_readings = total_sensors * 24  # Assuming 1 reading per hour per sensor
    uptime_percentage = min(100, (readings_last_24h / max(total_expected_readings, 1)) * 100)
    
    # Environmental averages across all buildings
    avg_temperature = SensorReading.objects.filter(
        name__sys__obj__company=request.user.company,
        name__name__icontains='температур',
        date__gte=last_24h
    ).aggregate(avg=Avg('value'))['avg']
    
    avg_humidity = SensorReading.objects.filter(
        name__sys__obj__company=request.user.company,
        name__name__icontains='влажн',
        date__gte=last_24h
    ).aggregate(avg=Avg('value'))['avg']
    
    # Prepare context
    context = {
        'profile': profile,
        'buildings': buildings,
        'honeycomb_buildings': json.dumps(honeycomb_buildings),
        'statistics': {
            'total_buildings': total_buildings,
            'total_sensors': total_sensors,
            'active_alerts': active_alerts,
            'uptime_percentage': round(uptime_percentage, 1),
            'avg_temperature': round(avg_temperature, 1) if avg_temperature else None,
            'avg_humidity': round(avg_humidity, 1) if avg_humidity else None,
        },
        'building_statuses': building_statuses,
        'recent_alerts': recent_alerts,
        'activity_metrics': {
            'readings_last_hour': readings_last_hour,
            'readings_last_24h': readings_last_24h,
        },
        'page_title': 'Dashboard V2',
        'dashboard_version': 'v2'
    }
    
    return render(request, 'dashboard/v2/main.html', context)


@login_required
@require_http_methods(["POST"])
def update_user_theme(request):
    """
    Update user theme preference via AJAX
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'dark')
        
        if theme not in ['dark', 'light']:
            return JsonResponse({'error': 'Invalid theme'}, status=400)
        
        # request.user is already UserProfile
        profile = request.user
        profile.theme = theme
        profile.save()
        
        return JsonResponse({
            'success': True,
            'theme': theme,
            'message': f'Theme updated to {theme}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def building_detail_v2(request, building_id):
    """
    Detailed building view with sensors and analytics
    """
    if request.user.role == 'superadmin':
        building = get_object_or_404(Building, id=building_id)
    else:
        building = get_object_or_404(Building, id=building_id, company=request.user.company)
    
    # Get all sensors for this building
    sensors = Sensor.objects.filter(building=building).select_related('sensor_type')
    
    # Get recent readings for charts (last 24 hours)
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    readings = SensorReading.objects.filter(
        name__sys__obj=building,
        date__gte=last_24h
    ).select_related('name', 'name__sys').order_by('date')
    
    # Organize readings by sensor for charts
    chart_data = {}
    for reading in readings:
        sensor_name = reading.name.name
        if sensor_name not in chart_data:
            chart_data[sensor_name] = {
                'labels': [],
                'data': [],
                'unit': reading.name.units or '',
                'type': reading.name.name
            }
        
        chart_data[sensor_name]['labels'].append(
            reading.date.strftime('%H:%M')
        )
        chart_data[sensor_name]['data'].append(float(reading.value) if reading.value else 0)
    
    # Calculate building analytics
    status = get_building_status(building)
    
    # Get alerts for this building
    alerts = Alert.objects.filter(
        rule__attribute__sys__obj=building
    ).select_related('rule', 'rule__attribute').order_by('-triggered_at')[:20]
    
    context = {
        'building': building,
        'sensors': sensors,
        'status': status,
        'chart_data': json.dumps(chart_data),
        'alerts': alerts,
        'page_title': f'{building.name} - Building Details',
        'dashboard_version': 'v2'
    }
    
    return render(request, 'dashboard/v2/building_detail.html', context)


@login_required
def honeycomb_data_api(request):
    """
    API endpoint for real-time honeycomb map data
    """
    if request.user.role == 'superadmin':
        buildings = Building.objects.all()
    else:
        buildings = Building.objects.filter(company=request.user.company)
    
    honeycomb_data = []
    for building in buildings:
        sensors = Sensor.objects.filter(building=building)
        sensor_count = sensors.count()
        
        status = get_building_status(building)
        
        # Get latest environmental readings
        temp_reading = None
        humidity_reading = None
        
        if sensor_count > 0:
            temp_sensor = sensors.filter(sensor_type__name__icontains='temperature').first()
            if temp_sensor:
                temp_reading = SensorReading.objects.filter(
                    sensor=temp_sensor
                ).order_by('-timestamp').first()
            
            humidity_sensor = sensors.filter(sensor_type__name__icontains='humidity').first()
            if humidity_sensor:
                humidity_reading = SensorReading.objects.filter(
                    sensor=humidity_sensor
                ).order_by('-timestamp').first()
        
        honeycomb_data.append({
            'id': f'building-{building.id}',
            'name': building.name,
            'status': status,
            'sensorCount': sensor_count,
            'temperature': float(temp_reading.value) if temp_reading else None,
            'humidity': float(humidity_reading.value) if humidity_reading else None,
            'icon': get_building_icon(building),
            'lastUpdate': temp_reading.date.isoformat() if temp_reading else None
        })
    
    return JsonResponse({
        'buildings': honeycomb_data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
def dashboard_stats_api(request):
    """
    API endpoint for dashboard statistics updates
    """
    # Calculate real-time statistics
    if request.user.role == 'superadmin':
        buildings = Building.objects.all()
        total_sensors = Sensor.objects.count()
        active_alerts = Alert.objects.filter(status='active').count()
    else:
        buildings = Building.objects.filter(company=request.user.company)
        total_sensors = Sensor.objects.filter(sys__obj__company=request.user.company).count()
        active_alerts = Alert.objects.filter(
            rule__attribute__sys__obj__company=request.user.company,
            status='active'
        ).count()
    
    total_buildings = buildings.count()
    
    # Recent activity
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    if request.user.role == 'superadmin':
        recent_readings = SensorReading.objects.filter(date__gte=last_hour).count()
    else:
        recent_readings = SensorReading.objects.filter(
            name__sys__obj__company=request.user.company,
            date__gte=last_hour
        ).count()
    
    # Building status distribution
    statuses = {'healthy': 0, 'warning': 0, 'critical': 0, 'offline': 0}
    for building in buildings:
        status = get_building_status(building)
        statuses[status] += 1
    
    return JsonResponse({
        'total_buildings': total_buildings,
        'total_sensors': total_sensors,
        'active_alerts': active_alerts,
        'recent_readings': recent_readings,
        'building_statuses': statuses,
        'timestamp': now.isoformat()
    })


def get_building_icon(building):
    """
    Get appropriate icon for building type
    """
    # For now, use default office icon since Obj model doesn't have building_type
    # TODO: Add building_type field to Obj model in future
    building_name = building.obj.lower() if building.obj else ''
    
    if 'склад' in building_name or 'warehouse' in building_name:
        return '🏭'
    elif 'цод' in building_name or 'datacenter' in building_name or 'сервер' in building_name:
        return '💻'
    elif 'лаб' in building_name or 'laboratory' in building_name:
        return '🔬'
    elif 'архив' in building_name or 'archive' in building_name:
        return '📚'
    else:
        return '🏢'  # Default office icon


# WebSocket consumer for real-time updates (if using Django Channels)
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.company_id = self.scope['user'].company.id
        self.group_name = f'dashboard_{self.company_id}'
        
        # Join company dashboard group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave company dashboard group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'request_update':
            # Send updated dashboard data
            await self.send_dashboard_update()
    
    async def send_dashboard_update(self):
        # This would be called by Celery tasks when new sensor data arrives
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': {
                'timestamp': timezone.now().isoformat(),
                'message': 'Dashboard data updated'
            }
        }))
    
    async def dashboard_update(self, event):
        # Receive message from room group
        await self.send(text_data=json.dumps(event['data']))

# Additional Dashboard V2 Views

@login_required
def buildings_list_v2(request):
    """Buildings list view"""
    if request.user.role == 'superadmin':
        buildings = Building.objects.all()
    else:
        buildings = Building.objects.filter(company=request.user.company)
    
    # Add counts for each building
    for building in buildings:
        building.systems_count = SensorSystem.objects.filter(obj=building).count()
        building.sensors_count = Sensor.objects.filter(sys__obj=building).count()
        building.status = get_building_status(building)
    
    context = {
        'buildings': buildings,
        'page_title': 'Buildings'
    }
    return render(request, 'dashboard/v2/buildings.html', context)


@login_required
def sensors_list_v2(request):
    """Sensors list view with Modbus connections"""
    if request.user.role == 'superadmin':
        sensors = Sensor.objects.all().select_related('sys__obj')
        modbus_connections = ModbusConnection.objects.all().select_related('building')
    else:
        sensors = Sensor.objects.filter(sys__obj__company=request.user.company).select_related('sys__obj')
        modbus_connections = ModbusConnection.objects.filter(building__company=request.user.company).select_related('building')
    
    # Add latest readings to sensors
    for sensor in sensors:
        latest_reading = SensorReading.objects.filter(name=sensor).order_by('-date').first()
        if latest_reading:
            sensor.latest_value = latest_reading.value
            sensor.last_update = latest_reading.date
            sensor.status = 'healthy' if abs(latest_reading.value) < 1000 else 'warning'
        else:
            sensor.latest_value = None
            sensor.last_update = None
            sensor.status = 'inactive'
    
    context = {
        'sensors': sensors,
        'modbus_connections': modbus_connections,
        'page_title': 'Sensors & Modbus'
    }
    return render(request, 'dashboard/v2/sensors.html', context)


@login_required
def alerts_list_v2(request):
    """Alerts list view"""
    if request.user.role == 'superadmin':
        alerts = Alert.objects.all().order_by('-triggered_at')
    else:
        alerts = Alert.objects.filter(rule__attribute__sys__obj__company=request.user.company).order_by('-triggered_at')
    context = {
        'alerts': alerts,
        'page_title': 'Alerts'
    }
    return render(request, 'dashboard/v2/alerts.html', context)


@login_required
def reports_list_v2(request):
    """Reports list view"""
    context = {
        'page_title': 'Reports'
    }
    return render(request, 'dashboard/v2/reports.html', context)


@login_required
def analytics_v2(request):
    """Analytics view"""
    context = {
        'page_title': 'Analytics'
    }
    return render(request, 'dashboard/v2/analytics.html', context)


@login_required
def settings_v2(request):
    """Settings view"""
    context = {
        'page_title': 'Settings',
        'user': request.user
    }
    return render(request, 'dashboard/v2/settings.html', context)


@login_required
def users_list_v2(request):
    """Users list view"""
    if request.user.role in ['superadmin', 'admin']:
        if request.user.role == 'superadmin':
            users = UserProfile.objects.all()
        else:
            users = UserProfile.objects.filter(company=request.user.company)
        context = {
            'users': users,
            'page_title': 'Users'
        }
        return render(request, 'dashboard/v2/users.html', context)
    else:
        return render(request, 'dashboard/v2/access_denied.html')
