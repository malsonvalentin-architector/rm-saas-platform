"""
ADMIN ПАНЕЛЬ ДЛЯ SaaS ПЛАТФОРМЫ
Обновленная версия с регистрацией всех моделей
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User_profile, Company, SubscriptionPlan, Subscription, AddonModule, Payment,
    Obj, System, Atributes, Data, AlertRule, Actuator, ActuatorCommand
)
from .forms import UserCreationForm, UserChangeForm


# ============================================================================
# ADMIN: КОМПАНИИ И ПОДПИСКИ
# ============================================================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscription_status_badge', 'systems_count', 
                   'users_count', 'created_at', 'is_active')
    list_filter = ('subscription_status', 'is_active', 'created_at', 'country')
    search_fields = ('name', 'legal_name', 'inn', 'contact_email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'legal_name', 'inn', 'is_active')
        }),
        ('Контакты', {
            'fields': ('contact_person', 'contact_email', 'contact_phone', 
                      'address', 'city', 'country')
        }),
        ('Подписка', {
            'fields': ('subscription_status', 'trial_ends_at', 'subscription_expires_at')
        }),
        ('Кастомизация', {
            'fields': ('logo', 'primary_color', 'secondary_color', 'custom_domain'),
            'classes': ('collapse',)
        }),
        ('Telegram', {
            'fields': ('telegram_enabled', 'telegram_chat_id'),
            'classes': ('collapse',)
        }),
        ('Системные поля', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subscription_status_badge(self, obj):
        colors = {
            'trial': 'orange',
            'active': 'green',
            'expired': 'red',
            'cancelled': 'gray',
            'suspended': 'darkred',
        }
        color = colors.get(obj.subscription_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_subscription_status_display()
        )
    subscription_status_badge.short_description = 'Статус подписки'
    
    def systems_count(self, obj):
        return obj.get_systems_count()
    systems_count.short_description = 'Систем'
    
    def users_count(self, obj):
        return obj.get_users_count()
    users_count.short_description = 'Пользователей'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_yearly', 'max_objects', 
                   'max_systems', 'max_users', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'description', 'is_active', 'is_featured', 'sort_order')
        }),
        ('Цены', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Лимиты', {
            'fields': ('max_objects', 'max_systems', 'max_users', 'max_data_retention_days')
        }),
        ('Возможности', {
            'fields': ('has_api_access', 'has_custom_reports', 'has_white_label', 
                      'has_priority_support', 'has_sla')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'status', 'total_price', 'billing_period', 
                   'paid_until', 'current_period_end')
    list_filter = ('status', 'billing_period')
    search_fields = ('company__name', 'plan__name')
    readonly_fields = ('base_price', 'addons_price', 'total_price', 'created_at', 'updated_at')
    date_hierarchy = 'current_period_start'
    filter_horizontal = ('addon_modules',)
    
    fieldsets = (
        ('Основное', {
            'fields': ('company', 'plan', 'status')
        }),
        ('Модули', {
            'fields': ('addon_modules',)
        }),
        ('Цены', {
            'fields': ('billing_period', 'base_price', 'addons_price', 'total_price')
        }),
        ('Период подписки', {
            'fields': ('trial_ends_at', 'current_period_start', 'current_period_end', 
                      'paid_until', 'cancelled_at')
        }),
        ('Заметки', {
            'fields': ('notes',)
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AddonModule)
class AddonModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_type', 'tier', 'price_monthly', 'is_active', 'is_coming_soon')
    list_filter = ('module_type', 'tier', 'is_active', 'is_coming_soon')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Основное', {
            'fields': ('module_type', 'tier', 'name', 'description', 'price_monthly')
        }),
        ('Характеристики AI Assistant', {
            'fields': ('ai_requests_limit',),
            'classes': ('collapse',)
        }),
        ('Характеристики Predictive Analytics', {
            'fields': ('prediction_accuracy', 'prediction_days'),
            'classes': ('collapse',)
        }),
        ('Характеристики Autonomous Optimization', {
            'fields': ('energy_saving_min', 'energy_saving_max', 'automation_level'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active', 'is_coming_soon', 'sort_order')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'status', 'payment_method', 'paid_at', 'created_at')
    list_filter = ('status', 'payment_method', 'paid_at')
    search_fields = ('subscription__company__name', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


# ============================================================================
# ADMIN: ПОЛЬЗОВАТЕЛИ
# ============================================================================

@admin.register(User_profile)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User_profile
    
    list_display = ('email', 'company', 'role', 'phone_number', 
                   'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'company')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name', 'company__name')
    ordering = ('company', 'email')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Компания и роль', {'fields': ('company', 'role')}),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'phone_number', 'position', 'department')
        }),
        ('Уведомления', {
            'fields': ('email_notifications', 'telegram_notifications', 'telegram_chat_id'),
            'classes': ('collapse',)
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company', 'role', 'phone_number', 'password1', 'password2')
        }),
    )


# ============================================================================
# ADMIN: ОБЪЕКТЫ И СИСТЕМЫ
# ============================================================================

@admin.register(Obj)
class ObjAdmin(admin.ModelAdmin):
    list_display = ('obj', 'company', 'city', 'is_active', 'created_at')
    list_filter = ('is_active', 'company', 'city')
    search_fields = ('obj', 'description', 'address', 'company__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основное', {
            'fields': ('obj', 'company', 'description', 'is_active')
        }),
        ('Местоположение', {
            'fields': ('address', 'city', 'latitude', 'longitude')
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'obj', 'ipaddr', 'is_online', 'is_active', 
                   'last_poll_time', 'period')
    list_filter = ('is_active', 'is_online', 'obj__company')
    search_fields = ('name', 'description', 'ipaddr', 'obj__obj')
    readonly_fields = ('created_at', 'updated_at', 'last_poll_time')
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'obj', 'description')
        }),
        ('Подключение', {
            'fields': ('ipaddr', 'period')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_online', 'last_poll_time')
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Atributes)
class AtributesAdmin(admin.ModelAdmin):
    list_display = ('name', 'sys', 'uom', 'modbus_carel', 'write', 
                   'alarm_atr', 'created_at')
    list_filter = ('modbus_carel', 'write', 'alarm_atr', 'sys__obj__company')
    search_fields = ('name', 'description', 'sys__name', 'carel_reg')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'sys', 'description', 'uom')
        }),
        ('Регистры', {
            'fields': ('modbus_carel', 'register', 'carel_reg')
        }),
        ('Настройки', {
            'fields': ('write', 'alarm_atr', 'min_value', 'max_value')
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'date', 'created_at')
    list_filter = ('date', 'name__sys__obj__company')
    search_fields = ('name__name', 'name__sys__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    # Ограничиваем количество записей на странице для производительности
    list_per_page = 50


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'attribute', 'condition', 'threshold', 
                   'severity', 'enabled')
    list_filter = ('enabled', 'severity', 'condition', 'company')
    search_fields = ('name', 'description', 'company__name', 'attribute__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'company', 'attribute', 'description', 'enabled')
        }),
        ('Условие', {
            'fields': ('condition', 'threshold', 'severity')
        }),
        ('Уведомления', {
            'fields': ('notify_email', 'notify_telegram', 'notify_sms', 'recipients')
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ADMIN: УПРАВЛЕНИЕ УСТРОЙСТВАМИ (PHASE 4.4)
# ============================================================================

@admin.register(Actuator)
class ActuatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'actuator_type', 'sys', 'current_value_display', 
                   'is_online', 'is_active', 'last_command_at')
    list_filter = ('actuator_type', 'is_active', 'is_online', 'sys__obj__company')
    search_fields = ('name', 'description', 'sys__name', 'sys__obj__obj')
    readonly_fields = ('created_at', 'updated_at', 'last_command_at')
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'sys', 'actuator_type', 'description')
        }),
        ('Modbus настройки', {
            'fields': ('modbus_carel', 'register', 'carel_reg', 'register_type')
        }),
        ('Параметры управления', {
            'fields': ('min_value', 'max_value', 'default_value', 'uom')
        }),
        ('Текущее состояние', {
            'fields': ('current_value', 'last_command_at', 'is_active', 'is_online')
        }),
        ('Системные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_value_display(self, obj):
        """Отображение текущего значения с цветом"""
        if obj.current_value is None:
            return format_html('<span style="color: gray;">N/A</span>')
        
        if obj.is_binary():
            color = 'green' if obj.current_value > 0 else 'gray'
            text = 'ВКЛ' if obj.current_value > 0 else 'ВЫКЛ'
        else:
            color = 'blue'
            text = f"{obj.current_value:.1f} {obj.uom}"
        
        return format_html(f'<span style="color: {color}; font-weight: bold;">{text}</span>')
    
    current_value_display.short_description = 'Значение'


@admin.register(ActuatorCommand)
class ActuatorCommandAdmin(admin.ModelAdmin):
    list_display = ('actuator', 'command_value', 'user', 'executed_at', 
                   'status_badge', 'response_time_ms', 'source_ip')
    list_filter = ('status', 'executed_at', 'actuator__actuator_type', 'actuator__sys__obj__company')
    search_fields = ('actuator__name', 'user__email', 'notes', 'error_message')
    readonly_fields = ('executed_at', 'actuator', 'user', 'source_ip')
    date_hierarchy = 'executed_at'
    
    # Ограничиваем количество записей для производительности
    list_per_page = 100
    
    fieldsets = (
        ('Команда', {
            'fields': ('actuator', 'command_value', 'user', 'executed_at', 'source_ip')
        }),
        ('Результат', {
            'fields': ('status', 'response_time_ms', 'error_message')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
    )
    
    def status_badge(self, obj):
        """Отображение статуса с цветом"""
        colors = {
            'pending': 'orange',
            'success': 'green',
            'failed': 'red',
            'timeout': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    
    status_badge.short_description = 'Статус'
    
    def has_add_permission(self, request):
        """Запретить ручное создание команд через админку"""
        return False


# ============================================================
# MODBUS INTEGRATION ADMIN
# Added: Phase 4.6 - Modbus Integration
# ============================================================

from data.models import ModbusConnection, ModbusRegisterMap, ModbusConnectionLog

@admin.register(ModbusConnection)
class ModbusConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'port', 'enabled', 'created_at']
    list_filter = ['enabled', 'protocol']
    search_fields = ['name', 'host']

@admin.register(ModbusRegisterMap)
class ModbusRegisterMapAdmin(admin.ModelAdmin):
    list_display = ['connection', 'sensor_name', 'register_type', 'address', 'enabled']
    list_filter = ['enabled', 'register_type', 'connection']
    search_fields = ['sensor_name', 'connection__name']

@admin.register(ModbusConnectionLog)
class ModbusConnectionLogAdmin(admin.ModelAdmin):
    list_display = ['connection', 'status', 'registers_read', 'created_at']
    list_filter = ['status', 'connection']
    readonly_fields = ['connection', 'status', 'message', 'created_at']
    
    def has_add_permission(self, request):
        return False

