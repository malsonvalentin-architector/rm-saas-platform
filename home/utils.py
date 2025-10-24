"""
ProMonitor V2 - Dashboard Utilities
Helper functions for building status calculation and sensor health monitoring
"""

from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q
from data.models import System as SensorSystem, Atributes as Sensor, Data as SensorReading, AlertEvent as Alert


def get_building_status(building):
    """
    Calculate overall building status based on sensors and alerts
    Returns: 'healthy', 'warning', 'critical', or 'offline'
    """
    sensors = Sensor.objects.filter(sys__obj=building)
    
    if not sensors.exists():
        return 'offline'
    
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    
    # Check for critical alerts in last 24 hours
    critical_alerts = Alert.objects.filter(
        rule__attribute__sys__obj=building,
        status='active',
        triggered_at__gte=last_24h
    ).count()
    
    if critical_alerts > 0:
        return 'critical'
    
    # Check for warning alerts (assuming we can identify warning level alerts)
    warning_alerts = Alert.objects.filter(
        rule__attribute__sys__obj=building,
        status__in=['active', 'acknowledged'],
        triggered_at__gte=last_24h
    ).count() - critical_alerts  # Subtract critical to avoid double counting
    
    # Check sensor activity (sensors that haven't reported in last hour)
    inactive_sensors = 0
    total_sensors = sensors.count()
    
    for sensor in sensors:
        latest_reading = SensorReading.objects.filter(
            name=sensor
        ).order_by('-date').first()
        
        if not latest_reading or latest_reading.date < last_hour:
            inactive_sensors += 1
    
    # Calculate health percentage
    if total_sensors > 0:
        active_percentage = ((total_sensors - inactive_sensors) / total_sensors) * 100
    else:
        active_percentage = 0
    
    # Determine status based on alerts and sensor activity
    if warning_alerts > 0 or active_percentage < 80:
        return 'warning'
    elif active_percentage < 50:
        return 'critical'
    elif active_percentage == 0:
        return 'offline'
    else:
        return 'healthy'


def calculate_sensor_health(sensor):
    """
    Calculate individual sensor health status
    Returns: 'healthy', 'warning', 'critical', or 'offline'
    """
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    
    # Get latest reading
    latest_reading = SensorReading.objects.filter(
        name=sensor
    ).order_by('-date').first()
    
    if not latest_reading:
        return 'offline'
    
    # Check if sensor is offline (no data in last hour)
    if latest_reading.date < last_hour:
        return 'offline'
    
    # Check for recent alerts
    recent_alerts = Alert.objects.filter(
        rule__attribute=sensor,
        status='active',
        triggered_at__gte=last_24h
    )
    
    # For now, treat all active alerts as critical
    # TODO: Implement severity levels in AlertRule model
    critical_alerts = recent_alerts.count()
    warning_alerts = 0
    
    if critical_alerts > 0:
        return 'critical'
    elif warning_alerts > 0:
        return 'warning'
    
    # Check value thresholds using sensor min/max values
    if latest_reading and (sensor.min_value is not None or sensor.max_value is not None):
        value = float(latest_reading.value)
        
        # Check against sensor-specific thresholds
        if sensor.max_value is not None and value > sensor.max_value:
            return 'critical'
        elif sensor.min_value is not None and value < sensor.min_value:
            return 'critical'
        
        # Temperature checks (assuming Celsius) - fallback for sensors without thresholds
        if 'temperature' in sensor.name.lower() or 'темп' in sensor.name.lower():
            if value > 35 or value < 5:  # Extreme temperatures
                return 'critical'
            elif value > 30 or value < 10:  # High/low temperatures
                return 'warning'
        
        # Humidity checks
        elif 'humidity' in sensor.name.lower() or 'влаж' in sensor.name.lower():
            if value > 90 or value < 10:  # Extreme humidity
                return 'critical'
            elif value > 80 or value < 20:  # High/low humidity
                return 'warning'
        
        # CO2 checks (ppm)
        elif 'co2' in sensor.name.lower():
            if value > 1000:  # High CO2
                return 'critical'
            elif value > 800:  # Elevated CO2
                return 'warning'
    
    return 'healthy'


def get_building_analytics(building, hours=24):
    """
    Get comprehensive analytics for a building
    """
    now = timezone.now()
    time_range = now - timedelta(hours=hours)
    
    sensors = Sensor.objects.filter(sys__obj=building)
    readings = SensorReading.objects.filter(
        name__sys__obj=building,
        date__gte=time_range
    )
    
    analytics = {
        'total_sensors': sensors.count(),
        'total_readings': readings.count(),
        'active_sensors': 0,
        'avg_temperature': None,
        'avg_humidity': None,
        'alert_count': 0,
        'sensor_details': []
    }
    
    # Calculate averages
    temp_readings = readings.filter(name__name__icontains='temperature')
    if temp_readings.exists():
        analytics['avg_temperature'] = temp_readings.aggregate(avg=Avg('value'))['avg']
    
    humidity_readings = readings.filter(name__name__icontains='humidity')
    if humidity_readings.exists():
        analytics['avg_humidity'] = humidity_readings.aggregate(avg=Avg('value'))['avg']
    
    # Count active sensors
    last_hour = now - timedelta(hours=1)
    for sensor in sensors:
        latest_reading = SensorReading.objects.filter(
            name=sensor
        ).order_by('-date').first()
        
        if latest_reading and latest_reading.date >= last_hour:
            analytics['active_sensors'] += 1
            
        # Add sensor details
        sensor_health = calculate_sensor_health(sensor)
        analytics['sensor_details'].append({
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.uom,  # Use unit of measurement as type for now
            'health': sensor_health,
            'latest_value': latest_reading.value if latest_reading else None,
            'latest_timestamp': latest_reading.date if latest_reading else None
        })
    
    # Count alerts
    analytics['alert_count'] = Alert.objects.filter(
        rule__attribute__sys__obj=building,
        triggered_at__gte=time_range
    ).count()
    
    return analytics


def get_company_overview(company):
    """
    Get company-wide overview statistics
    """
    buildings = company.obj_set.all()  # Related name for Obj model
    sensors = Sensor.objects.filter(sys__obj__company=company)
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_hour = now - timedelta(hours=1)
    
    overview = {
        'total_buildings': buildings.count(),
        'total_sensors': sensors.count(),
        'building_statuses': {
            'healthy': 0,
            'warning': 0,
            'critical': 0,
            'offline': 0
        },
        'active_alerts': 0,
        'readings_last_hour': 0,
        'system_uptime': 0,
        'avg_temperature': None,
        'avg_humidity': None
    }
    
    # Calculate building statuses
    for building in buildings:
        status = get_building_status(building)
        overview['building_statuses'][status] += 1
    
    # Count active alerts
    overview['active_alerts'] = Alert.objects.filter(
        rule__attribute__sys__obj__company=company,
        status='active'
    ).count()
    
    # Count recent readings
    overview['readings_last_hour'] = SensorReading.objects.filter(
        name__sys__obj__company=company,
        date__gte=last_hour
    ).count()
    
    # Calculate system uptime (percentage of expected readings received)
    expected_readings = sensors.count() * 24  # Assuming hourly readings
    actual_readings = SensorReading.objects.filter(
        name__sys__obj__company=company,
        date__gte=last_24h
    ).count()
    
    if expected_readings > 0:
        overview['system_uptime'] = min(100, (actual_readings / expected_readings) * 100)
    
    # Calculate environmental averages
    temp_avg = SensorReading.objects.filter(
        name__sys__obj__company=company,
        name__name__icontains='temperature',
        date__gte=last_24h
    ).aggregate(avg=Avg('value'))['avg']
    
    humidity_avg = SensorReading.objects.filter(
        name__sys__obj__company=company,
        name__name__icontains='humidity',
        date__gte=last_24h
    ).aggregate(avg=Avg('value'))['avg']
    
    overview['avg_temperature'] = round(temp_avg, 1) if temp_avg else None
    overview['avg_humidity'] = round(humidity_avg, 1) if humidity_avg else None
    
    return overview


def format_sensor_value(value, sensor_name, unit_of_measurement):
    """
    Format sensor value with appropriate precision and unit
    """
    if value is None:
        return 'N/A'
    
    try:
        num_value = float(value)
        
        # Use unit of measurement from sensor if available
        if unit_of_measurement:
            if '°C' in unit_of_measurement or 'celsius' in unit_of_measurement.lower():
                return f"{num_value:.1f}{unit_of_measurement}"
            elif '%' in unit_of_measurement:
                return f"{int(num_value)}{unit_of_measurement}"
            else:
                return f"{num_value:.2f} {unit_of_measurement}"
        
        # Fallback based on sensor name
        sensor_name_lower = sensor_name.lower()
        if 'temperature' in sensor_name_lower or 'темп' in sensor_name_lower:
            return f"{num_value:.1f}°C"
        elif 'humidity' in sensor_name_lower or 'влаж' in sensor_name_lower:
            return f"{int(num_value)}%"
        elif 'pressure' in sensor_name_lower or 'давл' in sensor_name_lower:
            return f"{num_value:.1f} hPa"
        elif 'co2' in sensor_name_lower:
            return f"{int(num_value)} ppm"
        else:
            return f"{num_value:.2f}"
            
    except (ValueError, TypeError):
        return str(value)


def get_status_color(status):
    """
    Get CSS color class for status
    """
    color_map = {
        'healthy': 'text-green-500',
        'warning': 'text-yellow-500',
        'critical': 'text-red-500',
        'offline': 'text-gray-500'
    }
    return color_map.get(status, 'text-gray-500')


def calculate_trend(readings, hours=24):
    """
    Calculate trend direction for sensor readings
    Returns: 'up', 'down', or 'stable'
    """
    if len(readings) < 2:
        return 'stable'
    
    # Compare first half vs second half of readings
    mid_point = len(readings) // 2
    first_half_avg = sum(r.value for r in readings[:mid_point]) / mid_point
    second_half_avg = sum(r.value for r in readings[mid_point:]) / (len(readings) - mid_point)
    
    difference = second_half_avg - first_half_avg
    threshold = abs(first_half_avg) * 0.05  # 5% threshold
    
    if difference > threshold:
        return 'up'
    elif difference < -threshold:
        return 'down'
    else:
        return 'stable'


def generate_alert_summary(company, hours=24):
    """
    Generate alert summary for dashboard
    """
    now = timezone.now()
    time_range = now - timedelta(hours=hours)
    
    alerts = Alert.objects.filter(
        rule__attribute__sys__obj__company=company,
        triggered_at__gte=time_range
    ).select_related('rule', 'rule__attribute', 'rule__attribute__sys', 'rule__attribute__sys__obj')
    
    summary = {
        'total_alerts': alerts.count(),
        'critical_alerts': alerts.filter(status='active').count(),  # Treat active as critical for now
        'warning_alerts': alerts.filter(status='acknowledged').count(),  # Treat acknowledged as warning
        'resolved_alerts': alerts.filter(status='resolved').count(),
        'recent_alerts': alerts.order_by('-triggered_at')[:5],
        'buildings_with_alerts': alerts.values('rule__attribute__sys__obj__obj').distinct().count()
    }
    
    return summary