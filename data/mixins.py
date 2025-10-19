"""
MIXINS ДЛЯ MULTI-TENANCY
Базовые классы для автоматической фильтрации данных по компании
"""

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404


class CompanyFilterMixin:
    """
    Автоматически фильтрует queryset по компании текущего пользователя
    """
    
    def get_queryset(self):
        """Фильтрует queryset по компании пользователя"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser:
            # Суперадмин видит все
            return queryset
        
        if not user.company:
            # Пользователь без компании не видит ничего
            return queryset.none()
        
        # Фильтруем по компании
        if hasattr(queryset.model, 'company'):
            return queryset.filter(company=user.company)
        elif hasattr(queryset.model, 'obj'):
            # Для System и Atributes фильтруем через obj
            return queryset.filter(obj__company=user.company)
        elif hasattr(queryset.model, 'name'):
            # Для Data фильтруем через атрибут
            return queryset.filter(name__sys__obj__company=user.company)
        
        return queryset


class CompanyRequiredMixin:
    """
    Требует, чтобы у пользователя была компания
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser and not request.user.company:
            messages.error(request, 'У вас нет доступа к этой странице. Обратитесь к администратору.')
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class SubscriptionRequiredMixin:
    """
    Требует активную подписку
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Суперадмин может все
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Проверяем компанию
        if not request.user.company:
            messages.error(request, 'У вас нет компании')
            return redirect('home')
        
        # Проверяем подписку
        if not request.user.company.is_subscription_active():
            messages.error(
                request, 
                'Подписка вашей компании истекла. Пожалуйста, продлите подписку.'
            )
            return redirect('subscription_expired')
        
        return super().dispatch(request, *args, **kwargs)


class CompanyAdminRequiredMixin:
    """
    Требует права администратора компании
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Суперадмин может все
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Проверяем права
        if not request.user.can_manage_company():
            raise PermissionDenied("Только администратор компании может выполнить это действие")
        
        return super().dispatch(request, *args, **kwargs)


class CompanyObjectMixin:
    """
    Автоматически устанавливает company при создании объекта
    """
    
    def form_valid(self, form):
        """Устанавливает company перед сохранением"""
        if hasattr(form.instance, 'company') and not form.instance.company:
            form.instance.company = self.request.user.company
        return super().form_valid(form)


class CompanyObjectAccessMixin:
    """
    Проверяет доступ к объекту (должен принадлежать компании пользователя)
    """
    
    def get_object(self, queryset=None):
        """Проверяет доступ к объекту"""
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Суперадмин может все
        if user.is_superuser:
            return obj
        
        # Проверяем принадлежность к компании
        if hasattr(obj, 'company'):
            if obj.company != user.company:
                raise Http404("Объект не найден")
        elif hasattr(obj, 'obj'):
            # Для System и Atributes
            if obj.obj.company != user.company:
                raise Http404("Объект не найден")
        elif hasattr(obj, 'name'):
            # Для Data
            if obj.name.sys.obj.company != user.company:
                raise Http404("Объект не найден")
        
        return obj


class LimitCheckMixin:
    """
    Проверяет лимиты подписки перед созданием объекта
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.method == 'POST':
            company = request.user.company
            
            if not company:
                messages.error(request, 'У вас нет компании')
                return redirect('home')
            
            # Получаем текущую подписку
            try:
                subscription = company.subscription
                plan = subscription.plan
            except:
                messages.error(request, 'У вашей компании нет активной подписки')
                return redirect('subscription_expired')
            
            # Проверяем лимиты в зависимости от модели
            model = self.model
            
            if model.__name__ == 'Obj':
                current_count = company.get_objects_count()
                if current_count >= plan.max_objects:
                    messages.error(
                        request,
                        f'Достигнут лимит объектов ({plan.max_objects}). '
                        f'Обновите тариф для добавления новых объектов.'
                    )
                    return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            elif model.__name__ == 'System':
                current_count = company.get_systems_count()
                if current_count >= plan.max_systems:
                    messages.error(
                        request,
                        f'Достигнут лимит систем ({plan.max_systems}). '
                        f'Обновите тариф для добавления новых систем.'
                    )
                    return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            elif model.__name__ == 'User_profile':
                current_count = company.get_users_count()
                if current_count >= plan.max_users:
                    messages.error(
                        request,
                        f'Достигнут лимит пользователей ({plan.max_users}). '
                        f'Обновите тариф для добавления новых пользователей.'
                    )
                    return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        return super().dispatch(request, *args, **kwargs)
