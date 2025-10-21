"""
Phase 4.2: CRUD Views for Objects Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Obj
from .permissions import role_required, can_create, can_edit, can_delete


@login_required
@role_required('superadmin', 'admin', 'manager')
def object_create(request):
    """Create new object (admin and manager only)"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            phone = request.POST.get('phone', '')
            description = request.POST.get('description', '')
            
            # Create object
            obj = Obj.objects.create(
                name=name,
                address=address,
                company=request.user.company,  # Assign to user's company
            )
            
            # Auto-create default systems for new object
            default_systems = [
                'HVAC (Климат-контроль)',
                'Электроснабжение',
                'Пожарная сигнализация',
            ]
            
            from .models import System, Atributes
            for sys_name in default_systems:
                system = System.objects.create(name=sys_name, obj=obj)
                
                # Create default sensors for each system
                if 'HVAC' in sys_name:
                    Atributes.objects.create(name='Температура', sys=system, uom='°C', write=False)
                    Atributes.objects.create(name='Влажность', sys=system, uom='%', write=False)
                    Atributes.objects.create(name='Мощность', sys=system, uom='кВт', write=False)
                elif 'Электро' in sys_name:
                    Atributes.objects.create(name='Напряжение', sys=system, uom='В', write=False)
                    Atributes.objects.create(name='Ток', sys=system, uom='А', write=False)
                    Atributes.objects.create(name='Мощность', sys=system, uom='кВт', write=False)
                elif 'Пожар' in sys_name:
                    Atributes.objects.create(name='Датчик дыма', sys=system, uom='', write=False)
                    Atributes.objects.create(name='Температура', sys=system, uom='°C', write=False)
            
            messages.success(request, f'Объект "{name}" успешно создан с {len(default_systems)} системами!')
            return redirect('data:object_dashboard', object_id=obj.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании объекта: {e}')
            return redirect('data:object_list')
    
    # GET request - show form
    return render(request, 'data/object_form.html', {
        'action': 'create',
        'title': 'Создать объект'
    })


@login_required
@role_required('superadmin', 'admin', 'manager')
def object_edit(request, object_id):
    """Edit existing object"""
    # Check access
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    if request.method == 'POST':
        try:
            # Update fields
            obj.name = request.POST.get('name', obj.name)
            obj.address = request.POST.get('address', obj.address)
            # Update other fields as needed
            obj.save()
            
            messages.success(request, f'Объект "{obj.name}" обновлён!')
            return redirect('data:object_dashboard', object_id=obj.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении: {e}')
    
    return render(request, 'data/object_form.html', {
        'object': obj,
        'action': 'edit',
        'title': f'Редактировать: {obj.name}'
    })


@login_required
@role_required('superadmin', 'admin')
def object_delete(request, object_id):
    """Delete object (admin only)"""
    # Check access
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f'Объект "{name}" удалён!')
        return redirect('data:object_list')
    
    return render(request, 'data/object_confirm_delete.html', {
        'object': obj
    })


# =============================================================================
# SYSTEMS CRUD (Phase 4.2)
# =============================================================================

@login_required
@role_required('superadmin', 'admin', 'manager', 'client')
def system_list(request, object_id):
    """List all systems for an object"""
    # Check access
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    # Get all systems with sensor counts
    from .models import System
    systems = System.objects.filter(obj=obj).prefetch_related('atributes_set')
    
    return render(request, 'data/system_list.html', {
        'object': obj,
        'systems': systems,
        'can_create': request.user.role in ['superadmin', 'admin', 'manager'],
    })


@login_required
@role_required('superadmin', 'admin', 'manager')
def system_create(request, object_id):
    """Create new system for an object"""
    # Check access to parent object
    if request.user.role == 'superadmin':
        obj = get_object_or_404(Obj, id=object_id)
    else:
        obj = get_object_or_404(Obj, id=object_id, company=request.user.company)
    
    if request.method == 'POST':
        try:
            from .models import System
            from datetime import timedelta
            
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            ipaddr = request.POST.get('ipaddr', '192.168.1.1')
            period_seconds = int(request.POST.get('period_seconds', 5))
            is_active = request.POST.get('is_active') == 'on'
            
            # Create system
            system = System.objects.create(
                name=name,
                description=description,
                ipaddr=ipaddr,
                obj=obj,
                period=timedelta(seconds=period_seconds),
                is_active=is_active,
            )
            
            messages.success(request, f'Система "{name}" успешно создана!')
            return redirect('data:system_list', object_id=obj.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании системы: {e}')
    
    return render(request, 'data/system_form.html', {
        'object': obj,
        'action': 'create',
        'title': f'Добавить систему для "{obj.obj}"'
    })


@login_required
@role_required('superadmin', 'admin', 'manager')
def system_edit(request, system_id):
    """Edit existing system"""
    from .models import System
    
    # Check access
    if request.user.role == 'superadmin':
        system = get_object_or_404(System, id=system_id)
    else:
        system = get_object_or_404(System, id=system_id, obj__company=request.user.company)
    
    if request.method == 'POST':
        try:
            from datetime import timedelta
            
            # Update fields
            system.name = request.POST.get('name', system.name)
            system.description = request.POST.get('description', system.description)
            system.ipaddr = request.POST.get('ipaddr', system.ipaddr)
            period_seconds = int(request.POST.get('period_seconds', 5))
            system.period = timedelta(seconds=period_seconds)
            system.is_active = request.POST.get('is_active') == 'on'
            system.save()
            
            messages.success(request, f'Система "{system.name}" обновлена!')
            return redirect('data:system_list', object_id=system.obj.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении: {e}')
    
    return render(request, 'data/system_form.html', {
        'object': system.obj,
        'system': system,
        'action': 'edit',
        'title': f'Редактировать систему: {system.name}',
        'period_seconds': int(system.period.total_seconds()),
    })


@login_required
@role_required('superadmin', 'admin')
def system_delete(request, system_id):
    """Delete system (admin only)"""
    from .models import System
    
    # Check access
    if request.user.role == 'superadmin':
        system = get_object_or_404(System, id=system_id)
    else:
        system = get_object_or_404(System, id=system_id, obj__company=request.user.company)
    
    if request.method == 'POST':
        obj_id = system.obj.id
        name = system.name
        sensors_count = system.atributes_set.count()
        system.delete()
        messages.success(request, f'Система "{name}" и {sensors_count} датчиков удалены!')
        return redirect('data:system_list', object_id=obj_id)
    
    return render(request, 'data/system_confirm_delete.html', {
        'system': system,
        'sensors_count': system.atributes_set.count(),
    })
