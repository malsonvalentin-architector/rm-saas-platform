"""
Phase 4.2: Global Systems Overview
Глобальная страница всех систем компании
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import System, Obj, Atributes


@login_required
def all_systems_overview(request):
    """
    Сводная страница всех систем компании
    Показывает статистику и таблицу всех систем
    """
    # Get all systems based on user role
    if request.user.role == 'superadmin':
        systems = System.objects.all()
        objects = Obj.objects.all()
    else:
        systems = System.objects.filter(obj__company=request.user.company)
        objects = Obj.objects.filter(company=request.user.company)
    
    # Annotate with sensor count
    systems = systems.select_related('obj').annotate(
        sensor_count=Count('atributes')
    ).order_by('-id')
    
    # Filters
    object_filter = request.GET.get('object', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if object_filter:
        systems = systems.filter(obj_id=object_filter)
    
    if status_filter == 'online':
        systems = systems.filter(is_active=True)
    elif status_filter == 'offline':
        systems = systems.filter(is_active=False)
    
    if search_query:
        systems = systems.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(obj__obj__icontains=search_query)
        )
    
    # Statistics
    total_systems = systems.count()
    online_systems = systems.filter(is_active=True).count()
    offline_systems = systems.filter(is_active=False).count()
    
    # Count systems with alerts (systems that have sensors with alerts)
    # TODO: Implement when AlertRule is connected
    alert_systems = 0
    
    # Total sensors across all systems
    total_sensors = sum(s.sensor_count for s in systems)
    
    context = {
        'systems': systems,
        'objects': objects,
        
        # Statistics
        'total_systems': total_systems,
        'online_systems': online_systems,
        'offline_systems': offline_systems,
        'alert_systems': alert_systems,
        'total_sensors': total_sensors,
        
        # Filters
        'object_filter': object_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        
        # Permissions
        'can_create': request.user.role in ['superadmin', 'admin', 'manager'],
        'can_edit': request.user.role in ['superadmin', 'admin', 'manager'],
    }
    
    return render(request, 'data/all_systems.html', context)
