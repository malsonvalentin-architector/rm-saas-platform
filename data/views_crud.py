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
                # Additional fields if exist in model
            )
            
            messages.success(request, f'Объект "{name}" успешно создан!')
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
