"""
OWNER V2: Обновленные базовые классы с поддержкой Multi-Tenancy
Замена старых Owner* классов на новые с фильтрацией по компании
"""

from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import (
    CompanyFilterMixin, 
    CompanyRequiredMixin, 
    SubscriptionRequiredMixin,
    CompanyObjectMixin,
    CompanyObjectAccessMixin,
    LimitCheckMixin
)


class OwnerListView(
    LoginRequiredMixin,
    CompanyRequiredMixin,
    SubscriptionRequiredMixin,
    CompanyFilterMixin,
    ListView
):
    """
    ListView с автоматической фильтрацией по компании пользователя
    """
    pass


class OwnerDetailView(
    LoginRequiredMixin,
    CompanyRequiredMixin,
    SubscriptionRequiredMixin,
    CompanyObjectAccessMixin,
    DetailView
):
    """
    DetailView с проверкой доступа к объекту
    """
    pass


class OwnerCreateView(
    LoginRequiredMixin,
    CompanyRequiredMixin,
    SubscriptionRequiredMixin,
    LimitCheckMixin,
    CompanyObjectMixin,
    CreateView
):
    """
    CreateView с автоматической установкой company и проверкой лимитов
    """
    
    def form_valid(self, form):
        """Устанавливает company перед сохранением"""
        object = form.save(commit=False)
        
        # Устанавливаем company если поле существует
        if hasattr(object, 'company') and not object.company:
            object.company = self.request.user.company
        
        # Старая логика для owner (для обратной совместимости)
        if hasattr(object, 'owner') and not object.owner:
            object.owner = self.request.user
        
        object.save()
        return super(CreateView, self).form_valid(form)


class OwnerUpdateView(
    LoginRequiredMixin,
    CompanyRequiredMixin,
    SubscriptionRequiredMixin,
    CompanyObjectAccessMixin,
    CompanyFilterMixin,
    UpdateView
):
    """
    UpdateView с проверкой доступа и фильтрацией по компании
    """
    pass


class OwnerDeleteView(
    LoginRequiredMixin,
    CompanyRequiredMixin,
    SubscriptionRequiredMixin,
    CompanyObjectAccessMixin,
    CompanyFilterMixin,
    DeleteView
):
    """
    DeleteView с проверкой доступа и фильтрацией по компании
    """
    pass


# References:
# https://docs.djangoproject.com/en/3.0/ref/class-based-views/mixins-editing/#django.views.generic.edit.ModelFormMixin.form_valid
# https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
# https://stackoverflow.com/a/15540149
# https://stackoverflow.com/questions/5531258/example-of-django-class-based-deleteview
