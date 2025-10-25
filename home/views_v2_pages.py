"""
ProMonitor V2 - Additional Pages Views
Buildings, Sensors, Alerts, Analytics, Reports, Settings, Users
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Max, Min
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from data.models import (
    Obj as Building, 
    System as SensorSystem, 
    Atributes as Sensor, 
    Data as SensorReading, 
    AlertEvent as Alert,
    AlertRule,
    User_profile as UserProfile,
    Company
)


# @login_required  # Temporary disabled for testing
def buildings_list(request):
    """Buildings List Page with search and filters"""
    
    # Get user's company buildings
    buildings = Building.objects.filter(is_active=True).select_related('company')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        buildings = buildings.filter(
            Q(obj__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        # Add your status logic here
        pass
    
    # Pagination
    paginator = Paginator(buildings, 12)  # 12 buildings per page
    page_number = request.GET.get('page', 1)
    buildings_page = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = {
        'total': buildings.count(),
        'active': buildings.filter(is_active=True).count(),
        'with_alerts': 0,  # Calculate based on your alert logic
    }
    
    context = {
        'buildings': buildings_page,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/v2/buildings.html', context)


# @login_required  # Temporary disabled for testing
def sensors_list(request):
    """Sensors List Page with Modbus integration info"""
    
    # Get all sensors with related systems
    sensors = Sensor.objects.select_related('sys', 'sys__obj').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        sensors = sensors.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sys__sys__icontains=search_query)
        )
    
    # Type filter
    type_filter = request.GET.get('type', 'all')
    if type_filter == 'modbus':
        sensors = sensors.filter(modbus_carel=True)
    elif type_filter == 'alarm':
        sensors = sensors.filter(alarm_atr=True)
    elif type_filter == 'writable':
        sensors = sensors.filter(write=True)
    
    # Building filter
    building_id = request.GET.get('building')
    if building_id:
        sensors = sensors.filter(sys__obj_id=building_id)
    
    # Pagination
    paginator = Paginator(sensors, 20)  # 20 sensors per page
    page_number = request.GET.get('page', 1)
    sensors_page = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = {
        'total': sensors.count(),
        'modbus': sensors.filter(modbus_carel=True).count(),
        'alarm_enabled': sensors.filter(alarm_atr=True).count(),
        'writable': sensors.filter(write=True).count(),
    }
    
    # Get buildings for filter dropdown
    buildings = Building.objects.filter(is_active=True).order_by('obj')
    
    context = {
        'sensors': sensors_page,
        'stats': stats,
        'search_query': search_query,
        'type_filter': type_filter,
        'buildings': buildings,
        'selected_building': building_id,
    }
    
    return render(request, 'dashboard/v2/sensors.html', context)


# @login_required  # Temporary disabled for testing
def alerts_list(request):
    """Alerts List Page with filtering and status management"""
    
    # Get all alerts with related data
    alerts = Alert.objects.select_related(
        'rule',
        'rule__sensor',
        'rule__sensor__sys',
        'acknowledged_by',
        'resolved_by'
    ).all()
    
    # Status filter
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        alerts = alerts.filter(status='active')
    elif status_filter == 'acknowledged':
        alerts = alerts.filter(status='acknowledged')
    elif status_filter == 'resolved':
        alerts = alerts.filter(status='resolved')
    elif status_filter != 'all':
        alerts = alerts.filter(status=status_filter)
    
    # Severity filter (from rule)
    severity_filter = request.GET.get('severity', 'all')
    if severity_filter != 'all':
        alerts = alerts.filter(rule__severity=severity_filter)
    
    # Time range filter
    time_range = request.GET.get('time_range', '24h')
    now = timezone.now()
    if time_range == '1h':
        alerts = alerts.filter(triggered_at__gte=now - timedelta(hours=1))
    elif time_range == '24h':
        alerts = alerts.filter(triggered_at__gte=now - timedelta(hours=24))
    elif time_range == '7d':
        alerts = alerts.filter(triggered_at__gte=now - timedelta(days=7))
    elif time_range == '30d':
        alerts = alerts.filter(triggered_at__gte=now - timedelta(days=30))
    
    # Order by most recent
    alerts = alerts.order_by('-triggered_at')
    
    # Pagination
    paginator = Paginator(alerts, 25)  # 25 alerts per page
    page_number = request.GET.get('page', 1)
    alerts_page = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = {
        'total': Alert.objects.count(),
        'active': Alert.objects.filter(status='active').count(),
        'acknowledged': Alert.objects.filter(status='acknowledged').count(),
        'resolved': Alert.objects.filter(status='resolved').count(),
        'critical': Alert.objects.filter(rule__severity='critical', status='active').count(),
    }
    
    context = {
        'alerts': alerts_page,
        'stats': stats,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'time_range': time_range,
    }
    
    return render(request, 'dashboard/v2/alerts.html', context)


# @login_required  # Temporary disabled for testing
def analytics_page(request):
    """Analytics Page with advanced charts and insights"""
    
    context = {
        'page_title': 'Analytics & Insights',
    }
    
    return render(request, 'dashboard/v2/analytics.html', context)


# @login_required  # Temporary disabled for testing
def reports_page(request):
    """Reports Page for generating custom reports"""
    
    context = {
        'page_title': 'Reports',
    }
    
    return render(request, 'dashboard/v2/reports.html', context)


# @login_required  # Temporary disabled for testing
def settings_page(request):
    """Settings Page for system configuration"""
    
    context = {
        'page_title': 'System Settings',
    }
    
    return render(request, 'dashboard/v2/settings.html', context)


# @login_required  # Temporary disabled for testing
def users_page(request):
    """Users Management Page"""
    
    # Get all users
    users = UserProfile.objects.select_related('company').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role', 'all')
    if role_filter != 'all':
        users = users.filter(role=role_filter)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    users_page = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = {
        'total': users.count(),
        'company_admin': users.filter(role='company_admin').count(),
        'operator': users.filter(role='operator').count(),
        'viewer': users.filter(role='viewer').count(),
    }
    
    context = {
        'users': users_page,
        'stats': stats,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    
    return render(request, 'dashboard/v2/users.html', context)
