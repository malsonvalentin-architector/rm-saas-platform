"""
VIEWS V2 - С ПОДДЕРЖКОЙ MULTI-TENANCY
Обновленная версия всех views с автоматической фильтрацией по компании
"""

from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import JsonResponse
from django.views import View
from django.contrib import messages

# НОВОЕ: Используем обновленные классы с multi-tenancy
from .owner_v2 import (
    OwnerListView, OwnerDetailView, OwnerCreateView, 
    OwnerUpdateView, OwnerDeleteView
)
from .mixins import CompanyFilterMixin, CompanyRequiredMixin, SubscriptionRequiredMixin

from .forms import CreateUserForm, CreateObjForm, CreateSystemForm, CreateAtribForm, CreateDataForm, WriteDataForm
from .models import User_profile, Obj, System, Atributes, Data, Company
from .utils.carel_req import get_carel_one_value, get_carel_all_values_json, set_carel_value
import json
from view_breadcrumbs import DetailBreadcrumbMixin, ListBreadcrumbMixin, UpdateBreadcrumbMixin


# ============================================================================
# USER VIEWS (обновлены для multi-tenancy)
# ============================================================================

class UserListView(ListBreadcrumbMixin, OwnerListView):
    """Список пользователей компании"""
    model = User_profile
    
    def get_queryset(self):
        """Показываем только пользователей своей компании"""
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset  # Суперадмин видит всех
        return queryset.filter(company=self.request.user.company)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ИСПРАВЛЕНО: Объекты компании, а не пользователя
        if self.request.user.company:
            context["objects"] = Obj.objects.filter(company=self.request.user.company)
        else:
            context["objects"] = Obj.objects.none()
        return context


class UserDetailView(OwnerDetailView):
    """Детальная информация о пользователе"""
    model = User_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # ИСПРАВЛЕНО: Объекты компании пользователя
        if user.company:
            context["objects"] = Obj.objects.filter(company=user.company)
        else:
            context["objects"] = Obj.objects.none()
        return context


class UserCreateView(CompanyRequiredMixin, CreateView):
    """Создание нового пользователя в компании"""
    model = User_profile
    form_class = CreateUserForm
    
    def form_valid(self, form):
        # Автоматически устанавливаем компанию
        form.instance.company = self.request.user.company
        # По умолчанию роль - оператор
        if not form.instance.role:
            form.instance.role = 'operator'
        return super().form_valid(form)
    
    def get_success_url(self):
        # После создания пользователя - на список пользователей
        return reverse_lazy('data:user_list')


class UserDeleteView(OwnerDeleteView):
    """Удаление пользователя (только своей компании)"""
    model = User_profile
    success_url = reverse_lazy('data:user_list')


class UserUpdateView(OwnerUpdateView):
    """Обновление данных пользователя"""
    model = User_profile
    form_class = CreateUserForm
    
    def get_success_url(self):
        return reverse_lazy('data:user_detail', kwargs={'pk': self.object.pk})


# ============================================================================
# OBJECT VIEWS (обновлены для multi-tenancy)
# ============================================================================

class ObjListView(OwnerListView):
    """Список объектов компании"""
    model = Obj


class ObjCreateView(OwnerCreateView):
    """Создание нового объекта"""
    model = Obj
    form_class = CreateObjForm
    
    def form_valid(self, form):
        # ИСПРАВЛЕНО: Устанавливаем company автоматически
        form.instance.company = self.request.user.company
        # Старое поле user оставляем для совместимости
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        # После создания объекта - на создание системы
        return reverse_lazy('data:sys_create', kwargs={'obj_pk': self.object.pk})


class ObjDetailView(OwnerDetailView):
    """Детальная информация об объекте"""
    model = Obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["systems"] = self.object.system_set.all()
        return context


class ObjDeleteView(OwnerDeleteView):
    """Удаление объекта (только своей компании)"""
    model = Obj
    success_url = reverse_lazy('data:user_list')


class ObjUpdateView(OwnerUpdateView):
    """Обновление данных объекта"""
    model = Obj
    form_class = CreateObjForm
    
    def get_success_url(self):
        return reverse_lazy('data:obj_detail', kwargs={'pk': self.object.pk})


# ============================================================================
# SYSTEM VIEWS (обновлены для multi-tenancy)
# ============================================================================

class SystemCreateView(OwnerCreateView):
    """Создание новой системы"""
    model = System
    form_class = CreateSystemForm
    
    def get_initial(self):
        initial = super().get_initial()
        obj = get_object_or_404(Obj, pk=self.kwargs['obj_pk'])
        
        # Проверяем что объект принадлежит компании пользователя
        if not self.request.user.is_superuser:
            if obj.company != self.request.user.company:
                raise PermissionDenied("Доступ запрещен")
        
        initial['obj'] = obj
        return initial
    
    def get_success_url(self):
        return reverse_lazy('data:atr_create', kwargs={
            'sys_pk': self.object.pk,
            'obj_pk': self.kwargs['obj_pk']
        })


class SystemDetailView(OwnerDetailView):
    """Детальная информация о системе"""
    model = System
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_data'] = self.object.obj
        return context


class SystemUpdateView(OwnerUpdateView):
    """Обновление данных системы"""
    model = System
    form_class = CreateSystemForm
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={
            'pk': self.object.pk,
            'obj_pk': self.object.obj.pk
        })


class SystemDeleteView(OwnerDeleteView):
    """Удаление системы"""
    model = System
    
    def get_success_url(self):
        return reverse_lazy('data:obj_detail', kwargs={'pk': self.object.obj.pk})


# ============================================================================
# ATTRIBUTE VIEWS (обновлены для multi-tenancy)
# ============================================================================

class AtribCreateView(OwnerCreateView):
    """Создание нового атрибута (датчика)"""
    model = Atributes
    form_class = CreateAtribForm
    
    def get_initial(self):
        initial = super().get_initial()
        system = get_object_or_404(System, pk=self.kwargs['sys_pk'])
        
        # Проверяем доступ через компанию
        if not self.request.user.is_superuser:
            if system.obj.company != self.request.user.company:
                raise PermissionDenied("Доступ запрещен")
        
        initial['sys'] = system
        return initial
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={
            'pk': self.kwargs['sys_pk'],
            'obj_pk': self.kwargs['obj_pk']
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['systems'] = get_object_or_404(System, pk=self.kwargs['sys_pk'])
        return context


class AtributeDetailView(CompanyRequiredMixin, DetailView):
    """Детальная информация об атрибуте с возможностью записи"""
    model = Atributes
    
    def get_queryset(self):
        """Фильтруем по компании"""
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(sys__obj__company=self.request.user.company)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.write:
            context['form'] = WriteDataForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка записи значения в CAREL контроллер"""
        self.object = self.get_object()
        
        # Проверка прав на запись
        if not request.user.can_control_equipment():
            messages.error(request, 'У вас нет прав на управление оборудованием')
            return redirect(self.request.path)
        
        form = WriteDataForm(request.POST)
        if form.is_valid():
            try:
                set_carel_value(
                    self.object.sys.ipaddr,
                    self.object.carel_reg,
                    form.cleaned_data['value']
                )
                messages.success(request, 'Значение успешно записано')
            except Exception as e:
                messages.error(request, f'Ошибка записи: {str(e)}')
            return redirect(self.request.path)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class AtributeListView(OwnerListView):
    """Список всех атрибутов компании"""
    model = Atributes
    template_name = 'data/atribute_list.html'


class AtribUpdateView(OwnerUpdateView):
    """Обновление данных атрибута"""
    model = Atributes
    form_class = CreateAtribForm
    
    def get_success_url(self):
        return reverse_lazy('data:atr_detail', kwargs={'pk': self.object.pk})


class AtibuteDeleteView(OwnerDeleteView):
    """Удаление атрибута"""
    model = Atributes
    
    def get_success_url(self):
        return reverse_lazy('data:sys_detail', kwargs={
            'pk': self.object.sys.pk,
            'obj_pk': self.object.sys.obj.pk
        })


# ============================================================================
# DATA VIEWS (работа с данными измерений)
# ============================================================================

class CreateDataView(CompanyRequiredMixin, CreateView):
    """Создание записи данных измерения"""
    model = Data
    form_class = CreateDataForm
    
    def get_initial(self):
        initial = super().get_initial()
        attribute = get_object_or_404(Atributes, pk=self.kwargs['atr_pk'])
        
        # Проверяем доступ
        if not self.request.user.is_superuser:
            if attribute.sys.obj.company != self.request.user.company:
                raise PermissionDenied("Доступ запрещен")
        
        # Получаем текущее значение с контроллера
        try:
            values = get_carel_one_value(attribute.sys.ipaddr, attribute.carel_reg)
            initial['value'] = values
        except Exception as e:
            messages.warning(self.request, f'Не удалось получить значение: {str(e)}')
        
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['atr_pk'] = self.kwargs['atr_pk']
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('data:atr_detail', kwargs={'pk': self.kwargs['atr_pk']})


# ============================================================================
# AJAX / API VIEWS (для динамических данных)
# ============================================================================

class GetCarelDataView(CompanyRequiredMixin, View):
    """AJAX view для получения данных с CAREL контроллера"""
    
    def get(self, request, *args, **kwargs):
        attribute = get_object_or_404(Atributes, pk=kwargs['atr_pk'])
        
        # Проверяем доступ к атрибуту
        if not request.user.is_superuser:
            if attribute.sys.obj.company != request.user.company:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            if kwargs.get('all_values'):
                # Получить все значения
                data = get_carel_all_values_json(attribute.sys.ipaddr)
            else:
                # Получить одно значение
                value = get_carel_one_value(attribute.sys.ipaddr, attribute.carel_reg)
                data = {
                    'attribute': attribute.name,
                    'value': value,
                    'uom': attribute.uom,
                }
            
            return JsonResponse(data, safe=False)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CompanyDashboardView(CompanyRequiredMixin, DetailView):
    """Dashboard компании со всей статистикой"""
    model = Company
    template_name = 'data/company_dashboard.html'
    
    def get_object(self):
        """Возвращаем компанию текущего пользователя"""
        if self.request.user.is_superuser:
            # Суперадмин может выбрать компанию
            pk = self.kwargs.get('pk')
            if pk:
                return get_object_or_404(Company, pk=pk)
        return self.request.user.company
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object
        
        # Статистика
        context['users_count'] = company.get_users_count()
        context['objects_count'] = company.get_objects_count()
        context['systems_count'] = company.get_systems_count()
        
        # Подписка
        try:
            context['subscription'] = company.subscription
            context['days_left'] = company.days_until_expiration()
        except:
            context['subscription'] = None
        
        # Последние объекты
        context['recent_objects'] = Obj.objects.filter(company=company).order_by('-created_at')[:5]
        
        # Последние данные
        context['recent_data'] = Data.objects.filter(
            name__sys__obj__company=company
        ).order_by('-date')[:10]
        
        return context
