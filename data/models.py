"""
МОДЕЛИ ДЛЯ SaaS ПЛАТФОРМЫ
Версия 2.0 с Multi-Tenancy и подписками
Phase 4.1: User Role System
"""

import datetime
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal


# ============================================================================
# НОВАЯ МОДЕЛЬ: КОМПАНИЯ (для Multi-Tenancy)
# ============================================================================

class Company(models.Model):
    """Компания-клиент платформы (Multi-Tenancy)"""
    
    # Основная информация
    name = models.CharField(max_length=200, verbose_name="Название компании")
    legal_name = models.CharField(max_length=300, blank=True, verbose_name="Юридическое название")
    inn = models.CharField(max_length=50, blank=True, verbose_name="ИНН/БИН")
    
    # Контактная информация
    contact_person = models.CharField(max_length=200, verbose_name="Контактное лицо")
    contact_email = models.EmailField(verbose_name="Email")
    contact_phone = PhoneNumberField(blank=True, verbose_name="Телефон")
    
    # Адрес
    address = models.TextField(blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    country = models.CharField(max_length=100, default='Казахстан', verbose_name="Страна")
    
    # Статус подписки
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Пробный период'),
            ('active', 'Активна'),
            ('expired', 'Истекла'),
            ('cancelled', 'Отменена'),
            ('suspended', 'Приостановлена'),
        ],
        default='trial',
        verbose_name="Статус подписки"
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    trial_ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Окончание пробного периода")
    subscription_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Окончание подписки")
    
    # Кастомизация (White-Label)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Логотип")
    primary_color = models.CharField(max_length=7, default='#007bff', verbose_name="Основной цвет")
    secondary_color = models.CharField(max_length=7, default='#6c757d', verbose_name="Дополнительный цвет")
    custom_domain = models.CharField(max_length=200, blank=True, verbose_name="Собственный домен")
    
    # Telegram интеграция
    telegram_chat_id = models.CharField(max_length=50, blank=True, verbose_name="Telegram Chat ID")
    telegram_enabled = models.BooleanField(default=False, verbose_name="Telegram уведомления")
    
    # Системные поля
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    
    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription_status', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def is_subscription_active(self):
        """Проверка активна ли подписка"""
        if not self.is_active:
            return False
            
        if self.subscription_status == 'trial':
            return timezone.now() < self.trial_ends_at if self.trial_ends_at else False
            
        return self.subscription_status == 'active' and (
            not self.subscription_expires_at or 
            timezone.now() < self.subscription_expires_at
        )
    
    def get_systems_count(self):
        """Количество систем компании"""
        from django.db.models import Count
        return System.objects.filter(obj__company=self).count()
    
    def get_users_count(self):
        """Количество пользователей компании"""
        return self.user_profile_set.count()
    
    def get_objects_count(self):
        """Количество объектов компании"""
        return self.obj_set.count()
    
    def days_until_expiration(self):
        """Дней до истечения подписки"""
        if self.subscription_status == 'trial' and self.trial_ends_at:
            return (self.trial_ends_at.date() - timezone.now().date()).days
        elif self.subscription_expires_at:
            return (self.subscription_expires_at.date() - timezone.now().date()).days
        return None


class User_profile(AbstractUser):
    """Пользователь с поддержкой Multi-Tenancy"""
    
    username = None
    email = models.EmailField("Email Address", unique=True)
    phone_number = PhoneNumberField(blank=True, verbose_name="Телефон")
    
    # НОВОЕ: Привязка к компании
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Компания"
    )
    
    # ОБНОВЛЕНО Phase 4.1: Новые роли
    role = models.CharField(
        max_length=20,
        choices=[
            ('superadmin', 'Superadmin'),
            ('admin', 'Company Admin'),
            ('manager', 'Manager'),
            ('client', 'Client'),
        ],
        default='client',
        verbose_name="Роль",
        help_text="Phase 4.1: Updated role system"
    )
    
    # Дополнительная информация
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name="Email уведомления")
    telegram_notifications = models.BooleanField(default=False, verbose_name="Telegram уведомления")
    telegram_chat_id = models.CharField(max_length=50, blank=True, verbose_name="Telegram Chat ID")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    # Phase 4.1: Role-based permission methods
    def is_superadmin(self):
        """Проверяет что пользователь - superadmin"""
        return self.role == 'superadmin'

    def is_company_admin(self):
        """Проверяет что пользователь - company admin"""
        return self.role in ['superadmin', 'admin']

    def is_manager(self):
        """Проверяет что пользователь - manager или выше"""
        return self.role in ['superadmin', 'admin', 'manager']

    def is_client(self):
        """Проверяет что пользователь - client"""
        return self.role == 'client'

    def can_manage_objects(self):
        """Право создавать/редактировать объекты"""
        return self.role in ['superadmin', 'admin', 'manager']

    def can_view_billing(self):
        """Право просматривать биллинг и подписки"""
        return self.role in ['superadmin', 'admin']

    def can_manage_subscription(self):
        """Право управлять подписками компании"""
        return self.role in ['superadmin', 'admin']

    def can_manage_users(self):
        """Право управлять пользователями компании"""
        return self.role in ['superadmin', 'admin']

    def get_accessible_companies(self):
        """Возвращает queryset компаний, доступных пользователю"""
        if self.role == 'superadmin':
            return Company.objects.all()
        elif self.company:
            return Company.objects.filter(id=self.company.id)
        else:
            return Company.objects.none()
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['company', 'email']
    
    def __str__(self):
        company_name = self.company.name if self.company else 'Без компании'
        return f"{self.email} ({company_name})"
    
    def can_manage_company(self):
        """Может ли управлять компанией"""
        return self.role == 'admin' or self.is_superuser
    
    def can_control_equipment(self):
        """Может ли управлять оборудованием"""
        return self.role in ['admin', 'manager'] or self.is_superuser
    
    def can_view_only(self):
        """Только просмотр"""
        return self.role == 'client'


class Obj(models.Model):
    """Объект (здание, помещение) - ОБНОВЛЕННАЯ ВЕРСИЯ"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    obj = models.CharField(max_length=200, verbose_name="Название объекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # СТАРОЕ ПОЛЕ (временно для миграции)
    user = models.ForeignKey(
        User_profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Пользователь (устаревшее)"
    )
    
    # НОВОЕ: Привязка к компании вместо пользователя
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Компания"
    )
    
    # Дополнительная информация
    address = models.CharField(max_length=300, blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    
    # Phase 4.3: Manager notes (только для manager role)
    manager_notes = models.TextField(blank=True, verbose_name="Заметки менеджера", help_text="Внутренние заметки о клиенте и объекте")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        ordering = ['company', 'obj']
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]
    
    def __str__(self):
        company_name = self.company.name if self.company else 'No Company'
        return f'{self.obj} ({company_name})'


class System(models.Model):
    """Система (контроллер CAREL)"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    
    name = models.CharField(max_length=50, verbose_name="Название системы")
    description = models.TextField(blank=True, verbose_name="Описание")
    ipaddr = models.GenericIPAddressField(protocol='IPv4', verbose_name="IP адрес")
    obj = models.ForeignKey(Obj, on_delete=models.CASCADE, verbose_name="Объект")
    period = models.DurationField(default=datetime.timedelta(seconds=5), verbose_name="Период опроса")
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    last_poll_time = models.DateTimeField(null=True, blank=True, verbose_name="Последний опрос")
    is_online = models.BooleanField(default=False, verbose_name="В сети")
    
    class Meta:
        verbose_name = "Система"
        verbose_name_plural = "Системы"
        ordering = ['obj', 'name']
        indexes = [
            models.Index(fields=['obj', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.obj}'


class Atributes(models.Model):
    """Атрибуты (датчики и параметры)"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    name = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    uom = models.CharField(max_length=10, verbose_name="Единица измерения")
    
    modbus_carel = models.BooleanField(verbose_name="Modbus/CAREL")
    
    # Типы регистров Modbus
    INPUT = 'IR'
    HOLDING = 'HD'
    COIL = 'CL'
    DISCRETE_IN = 'DI'
    modbus_reg_ch = {
        INPUT: "Input Register",
        HOLDING: "Holding Register",
        COIL: 'Coil',
        DISCRETE_IN: "Discrete Input"
    }
    
    register = models.IntegerField(null=True, blank=True, verbose_name="Регистр Modbus")
    carel_reg = models.CharField(null=True, blank=True, max_length=50, verbose_name="Переменная CAREL")
    
    sys = models.ForeignKey(System, on_delete=models.CASCADE, verbose_name="Система")
    
    write = models.BooleanField(default=False, verbose_name="Запись разрешена")
    alarm_atr = models.BooleanField(default=False, verbose_name="Тревожный параметр")
    
    # Лимиты для тревог
    min_value = models.FloatField(null=True, blank=True, verbose_name="Мин. значение")
    max_value = models.FloatField(null=True, blank=True, verbose_name="Макс. значение")
    
    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"
        ordering = ['sys', 'name']
    
    def get_value(self):
        return self.carel_reg if self.modbus_carel else self.register
    
    def clean(self):
        if self.modbus_carel and self.register is None:
            raise ValidationError("Integer value required when 'modbus_carel' is True")
        if not self.modbus_carel and not self.carel_reg:
            raise ValidationError("Char value required when 'modbus_carel' is False")
    
    def __str__(self):
        return f'{self.name} - {self.sys}'


class Data(models.Model):
    """Данные измерений"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    
    value = models.FloatField(null=True, blank=True, verbose_name="Значение")
    date = models.DateTimeField(null=True, default=timezone.now, verbose_name="Дата/время")
    name = models.ForeignKey(Atributes, on_delete=models.CASCADE, verbose_name="Атрибут")
    
    class Meta:
        verbose_name = "Данные"
        verbose_name_plural = "Данные"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['name', '-date']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f'{self.name} = {self.value} ({self.date})'


# ============================================================================
# ПРАВИЛА ТРЕВОГ
# ============================================================================

class AlertRule(models.Model):
    """Правило для автоматического создания тревог"""
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    attribute = models.ForeignKey(Atributes, on_delete=models.CASCADE, verbose_name="Атрибут")
    
    name = models.CharField(max_length=200, verbose_name="Название правила")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Условие
    condition = models.CharField(
        max_length=5,
        choices=[
            ('>', 'Больше'),
            ('<', 'Меньше'),
            ('>=', 'Больше или равно'),
            ('<=', 'Меньше или равно'),
            ('==', 'Равно'),
            ('!=', 'Не равно'),
        ],
        verbose_name="Условие"
    )
    threshold = models.FloatField(verbose_name="Пороговое значение")
    
    # Уровень серьезности
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Низкий'),
            ('medium', 'Средний'),
            ('high', 'Высокий'),
            ('critical', 'Критический'),
        ],
        verbose_name="Уровень"
    )
    
    # Каналы уведомлений
    notify_email = models.BooleanField(default=True, verbose_name="Email")
    notify_telegram = models.BooleanField(default=False, verbose_name="Telegram")
    notify_sms = models.BooleanField(default=False, verbose_name="SMS")
    
    # Получатели (JSON список email или telegram chat_id)
    recipients = models.TextField(blank=True, default="[]", verbose_name="Получатели")
    
    # Статус
    enabled = models.BooleanField(default=True, verbose_name="Включено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Правило тревоги"
        verbose_name_plural = "Правила тревог"
        ordering = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.attribute}"
    
    def check_condition(self, value):
        """Проверить выполняется ли условие"""
        conditions = {
            '>': value > self.threshold,
            '<': value < self.threshold,
            '>=': value >= self.threshold,
            '<=': value <= self.threshold,
            '==': value == self.threshold,
            '!=': value != self.threshold,
        }
        return conditions.get(self.condition, False)


class AlertEvent(models.Model):
    """История срабатываний тревог (Phase 4.3)"""
    
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name="Правило", related_name='events')
    
    # Информация о срабатывании
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Время срабатывания")
    value = models.FloatField(verbose_name="Значение при срабатывании")
    
    # Статус тревоги
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Активна'),
            ('acknowledged', 'Подтверждена'),
            ('resolved', 'Решена'),
            ('snoozed', 'Отложена'),
            ('ignored', 'Игнорирована'),
        ],
        default='active',
        verbose_name="Статус"
    )
    
    # Действия пользователей
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
        verbose_name="Подтверждена"
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="Время подтверждения")
    
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        verbose_name="Решена"
    )
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Время решения")
    
    # Отложить тревогу
    snooze_until = models.DateTimeField(null=True, blank=True, verbose_name="Отложена до")
    snoozed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='snoozed_alerts',
        verbose_name="Отложена"
    )
    
    # Дополнительная информация
    notes = models.TextField(blank=True, verbose_name="Заметки")
    
    class Meta:
        verbose_name = "Событие тревоги"
        verbose_name_plural = "События тревог"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status', '-triggered_at']),
            models.Index(fields=['rule', 'status']),
        ]
    
    def __str__(self):
        return f"{self.rule.name} - {self.get_status_display()} ({self.triggered_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_severity(self):
        """Получить уровень серьёзности из правила"""
        return self.rule.severity
    
    def get_duration(self):
        """Продолжительность активности тревоги"""
        if self.status == 'resolved' and self.resolved_at:
            return self.resolved_at - self.triggered_at
        return timezone.now() - self.triggered_at
    
    def is_snoozed(self):
        """Проверка отложена ли тревога"""
        if self.status == 'snoozed' and self.snooze_until:
            return timezone.now() < self.snooze_until
        return False
    
    def get_object_name(self):
        """Название объекта через атрибут → система → объект"""
        return self.rule.attribute.sys.obj.obj if self.rule.attribute.sys else "N/A"
    
    def get_system_name(self):
        """Название системы"""
        return self.rule.attribute.sys.name if self.rule.attribute.sys else "N/A"
    
    def get_sensor_name(self):
        """Название датчика"""
        return self.rule.attribute.name


class AlertComment(models.Model):
    """Комментарии к тревогам (Phase 4.3)"""
    
    event = models.ForeignKey(AlertEvent, on_delete=models.CASCADE, verbose_name="Тревога", related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    
    text = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    
    class Meta:
        verbose_name = "Комментарий к тревоге"
        verbose_name_plural = "Комментарии к тревогам"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.email}: {self.text[:50]}..."


# ============================================================================
# МОДЕЛИ ДЛЯ СИСТЕМЫ ПОДПИСОК (Subscription System)
# ============================================================================

class SubscriptionPlan(models.Model):
    """Базовые тарифные планы"""
    
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    price_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена в месяц ($)"
    )
    price_yearly = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Цена в год ($)"
    )
    
    max_objects = models.IntegerField(default=3, verbose_name="Максимум объектов")
    max_systems = models.IntegerField(default=10, verbose_name="Максимум систем")
    max_users = models.IntegerField(default=5, verbose_name="Максимум пользователей")
    max_data_retention_days = models.IntegerField(default=30, verbose_name="Хранение данных (дней)")
    
    has_api_access = models.BooleanField(default=False, verbose_name="API доступ")
    has_custom_reports = models.BooleanField(default=False, verbose_name="Кастомные отчёты")
    has_white_label = models.BooleanField(default=False, verbose_name="White-label брендинг")
    has_priority_support = models.BooleanField(default=False, verbose_name="Приоритетная поддержка")
    has_sla = models.BooleanField(default=False, verbose_name="SLA 99.9%")
    
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"
        ordering = ['sort_order', 'price_monthly']
    
    def __str__(self):
        return f"{self.name} (${self.price_monthly}/мес)"
    
    def get_yearly_discount_percent(self):
        if not self.price_yearly:
            return 0
        monthly_total = self.price_monthly * 12
        discount = monthly_total - self.price_yearly
        return round((discount / monthly_total) * 100)


class AddonModule(models.Model):
    """Дополнительные модули"""
    
    MODULE_TYPES = [
        ('ai_assistant', '🤖 AI Chat Assistant'),
        ('predictive', '🔮 Predictive Analytics'),
        ('optimization', '⚡ Autonomous Optimization'),
    ]
    
    TIER_CHOICES = [
        ('starter', 'Starter'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES, verbose_name="Тип модуля")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, verbose_name="Уровень")
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена в месяц ($)")
    
    ai_requests_limit = models.IntegerField(null=True, blank=True, verbose_name="Лимит AI запросов/месяц")
    prediction_accuracy = models.IntegerField(null=True, blank=True, verbose_name="Точность предсказаний (%)")
    prediction_days = models.IntegerField(null=True, blank=True, verbose_name="Горизонт прогноза (дней)")
    energy_saving_min = models.IntegerField(null=True, blank=True, verbose_name="Минимальная экономия (%)")
    energy_saving_max = models.IntegerField(null=True, blank=True, verbose_name="Максимальная экономия (%)")
    automation_level = models.CharField(max_length=50, blank=True, verbose_name="Уровень автоматизации")
    
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_coming_soon = models.BooleanField(default=False, verbose_name="Coming Soon")
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Дополнительный модуль"
        verbose_name_plural = "Дополнительные модули"
        ordering = ['module_type', 'sort_order']
        unique_together = ['module_type', 'tier']
    
    def __str__(self):
        return f"{self.get_module_type_display()} - {self.tier.upper()} (${self.price_monthly}/мес)"


class Subscription(models.Model):
    """Активная подписка компании"""
    
    BILLING_PERIODS = [
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно'),
    ]
    
    STATUS_CHOICES = [
        ('trial', 'Пробный период'),
        ('active', 'Активна'),
        ('past_due', 'Просрочен платёж'),
        ('cancelled', 'Отменена'),
        ('expired', 'Истекла'),
    ]
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='subscription', verbose_name="Компания")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, verbose_name="Тарифный план")
    addon_modules = models.ManyToManyField(AddonModule, blank=True, verbose_name="Дополнительные модули")
    
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIODS, default='monthly', verbose_name="Период оплаты")
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Базовая цена ($)")
    addons_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Цена модулей ($)")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Итоговая цена ($)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial', verbose_name="Статус")
    
    trial_ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Окончание trial")
    current_period_start = models.DateTimeField(auto_now_add=True, verbose_name="Начало периода")
    current_period_end = models.DateTimeField(null=True, blank=True, verbose_name="Конец периода")
    paid_until = models.DateTimeField(null=True, blank=True, verbose_name="Оплачено до")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата отмены")
    notes = models.TextField(blank=True, verbose_name="Заметки админа")
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} (${self.total_price}/мес)"
    
    def is_active(self):
        if self.status == 'trial':
            return timezone.now() < self.trial_ends_at if self.trial_ends_at else False
        
        if self.status != 'active':
            return False
        
        if self.paid_until:
            return timezone.now() < self.paid_until
        
        return timezone.now() < self.current_period_end
    
    def calculate_prices(self):
        if self.billing_period == 'yearly' and self.plan.price_yearly:
            self.base_price = self.plan.price_yearly / 12
        else:
            self.base_price = self.plan.price_monthly
        
        self.addons_price = sum(addon.price_monthly for addon in self.addon_modules.all())
        self.total_price = self.base_price + self.addons_price
    
    def save(self, *args, **kwargs):
        if self.pk:
            self.calculate_prices()
        super().save(*args, **kwargs)
    
    def days_until_expiry(self):
        target_date = self.paid_until or self.current_period_end
        if not target_date:
            return None
        delta = target_date - timezone.now()
        return delta.days if delta.days > 0 else 0
    
    def get_usage_stats(self):
        from django.db.models import Count
        
        objects_count = self.company.obj_set.count()
        systems_count = self.company.get_systems_count()
        users_count = self.company.user_set.count()
        
        return {
            'objects': {
                'used': objects_count,
                'limit': self.plan.max_objects,
                'percent': round((objects_count / self.plan.max_objects) * 100) if self.plan.max_objects else 0
            },
            'systems': {
                'used': systems_count,
                'limit': self.plan.max_systems,
                'percent': round((systems_count / self.plan.max_systems) * 100) if self.plan.max_systems else 0
            },
            'users': {
                'used': users_count,
                'limit': self.plan.max_users,
                'percent': round((users_count / self.plan.max_users) * 100) if self.plan.max_users else 0
            }
        }


class Payment(models.Model):
    """История платежей"""
    
    PAYMENT_STATUS = [
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', verbose_name="Подписка")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма ($)")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name="Статус")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Способ оплаты")
    transaction_id = models.CharField(max_length=200, blank=True, verbose_name="ID транзакции")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"${self.amount} - {self.subscription.company.name} ({self.get_status_display()})"
# ============================================================================
# PHASE 4.4: ACTUATORS & CONTROL SYSTEM (MVP Version)
# ============================================================================
# Философия: Steve Jobs MVP - начать с простого и элегантного
# - Базовая модель исполнительного устройства
# - Простая история команд
# - Готовность к расширению


class Actuator(models.Model):
    """
    Исполнительное устройство (Phase 4.4 MVP)
    
    Примеры:
    - Клапан (valve): открыть/закрыть, 0-100%
    - Реле (relay): вкл/выкл
    - Мотор (motor): скорость 0-100%
    - Выключатель (switch): вкл/выкл
    - Диммер (dimmer): яркость 0-100%
    """
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")
    
    # Привязка к системе (как у Atributes)
    sys = models.ForeignKey('System', on_delete=models.CASCADE, verbose_name="Система", related_name='actuators')
    
    # Основная информация
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Тип устройства
    ACTUATOR_TYPES = [
        ('valve', '🚰 Клапан'),
        ('relay', '⚡ Реле'),
        ('motor', '⚙️ Мотор'),
        ('switch', '💡 Выключатель'),
        ('dimmer', '🔆 Диммер'),
        ('pump', '💧 Насос'),
        ('fan', '🌀 Вентилятор'),
        ('heater', '🔥 Нагреватель'),
        ('cooler', '❄️ Охладитель'),
    ]
    actuator_type = models.CharField(
        max_length=20,
        choices=ACTUATOR_TYPES,
        verbose_name="Тип устройства"
    )
    
    # Modbus параметры (аналогично Atributes)
    modbus_carel = models.BooleanField(default=True, verbose_name="Modbus/CAREL")
    register = models.IntegerField(null=True, blank=True, verbose_name="Регистр Modbus")
    carel_reg = models.CharField(max_length=50, blank=True, verbose_name="Переменная CAREL")
    
    # Тип регистра для записи
    REGISTER_TYPES = [
        ('HD', 'Holding Register'),
        ('CL', 'Coil'),
    ]
    register_type = models.CharField(
        max_length=2,
        choices=REGISTER_TYPES,
        default='HD',
        verbose_name="Тип регистра"
    )
    
    # Параметры управления
    min_value = models.FloatField(default=0, verbose_name="Минимальное значение")
    max_value = models.FloatField(default=100, verbose_name="Максимальное значение")
    default_value = models.FloatField(default=0, verbose_name="Значение по умолчанию")
    
    # Текущее состояние
    current_value = models.FloatField(null=True, blank=True, verbose_name="Текущее значение")
    last_command_at = models.DateTimeField(null=True, blank=True, verbose_name="Последняя команда")
    
    # Единица измерения
    uom = models.CharField(max_length=20, blank=True, default='%', verbose_name="Ед. изм.")
    
    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_online = models.BooleanField(default=False, verbose_name="В сети")
    
    class Meta:
        verbose_name = "Исполнительное устройство"
        verbose_name_plural = "Исполнительные устройства"
        ordering = ['sys', 'name']
        indexes = [
            models.Index(fields=['sys', 'is_active']),
            models.Index(fields=['actuator_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_actuator_type_display()}) - {self.sys}"
    
    def is_binary(self):
        """Проверка: бинарное устройство (вкл/выкл)?"""
        return self.actuator_type in ['relay', 'switch', 'pump']
    
    def is_analog(self):
        """Проверка: аналоговое устройство (0-100%)?"""
        return self.actuator_type in ['valve', 'motor', 'dimmer', 'fan', 'heater', 'cooler']
    
    def get_display_value(self):
        """Отображаемое значение с единицами измерения"""
        if self.current_value is None:
            return "N/A"
        
        if self.is_binary():
            return "ВКЛ" if self.current_value > 0 else "ВЫКЛ"
        
        return f"{self.current_value:.1f} {self.uom}"
    
    def get_object_name(self):
        """Название объекта через систему → объект"""
        return self.sys.obj.obj if self.sys and self.sys.obj else "N/A"


class ActuatorCommand(models.Model):
    """
    История команд управления (Phase 4.4 MVP)
    
    Хранит:
    - Кто выполнил команду
    - Когда
    - Какое значение было установлено
    - Статус выполнения
    """
    
    # Привязка к устройству
    actuator = models.ForeignKey(
        Actuator,
        on_delete=models.CASCADE,
        verbose_name="Устройство",
        related_name='commands'
    )
    
    # Команда
    command_value = models.FloatField(verbose_name="Заданное значение")
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время выполнения")
    
    # Пользователь
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name='actuator_commands'
    )
    
    # Статус выполнения
    STATUS_CHOICES = [
        ('pending', '⏳ Ожидает'),
        ('success', '✅ Выполнена'),
        ('failed', '❌ Ошибка'),
        ('timeout', '⏱️ Таймаут'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    # Дополнительная информация
    response_time_ms = models.IntegerField(null=True, blank=True, verbose_name="Время отклика (мс)")
    error_message = models.TextField(blank=True, verbose_name="Сообщение об ошибке")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    # IP адрес источника команды (для аудита)
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP источника")
    
    class Meta:
        verbose_name = "Команда управления"
        verbose_name_plural = "Команды управления"
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['actuator', '-executed_at']),
            models.Index(fields=['user', '-executed_at']),
            models.Index(fields=['status', '-executed_at']),
        ]
    
    def __str__(self):
        user_name = self.user.email if self.user else "System"
        return f"{self.actuator.name}: {self.command_value} by {user_name} ({self.get_status_display()})"
    
    def get_duration(self):
        """Время с момента выполнения команды"""
        return timezone.now() - self.executed_at
    
    def is_recent(self):
        """Проверка: команда выполнена недавно (< 5 минут)?"""
        return self.get_duration().total_seconds() < 300


# ============================================================
# MODBUS INTEGRATION MODELS
# Added: Phase 4.6 - Modbus Integration
# ============================================================

from django.core.validators import MinValueValidator, MaxValueValidator


class ModbusConnection(models.Model):
    """
    Modbus TCP подключение к контроллеру или эмулятору
    """
    PROTOCOL_CHOICES = [
        ('tcp', 'Modbus TCP'),
        ('rtu', 'Modbus RTU over TCP'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Название подключения",
        help_text="Например: CAREL pCO Emulator"
    )
    
    host = models.CharField(
        max_length=255,
        verbose_name="Хост",
        help_text="IP адрес или hostname (например: localhost, 192.168.11.101)"
    )
    
    port = models.IntegerField(
        default=502,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name="Порт",
        help_text="Стандартный Modbus TCP порт: 502"
    )
    
    protocol = models.CharField(
        max_length=10,
        choices=PROTOCOL_CHOICES,
        default='tcp',
        verbose_name="Протокол"
    )
    
    slave_id = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(247)],
        verbose_name="Slave ID",
        help_text="ID устройства (обычно 1)"
    )
    
    timeout = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name="Таймаут (секунды)",
        help_text="Таймаут подключения"
    )
    
    poll_interval = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(3600)],
        verbose_name="Интервал опроса (секунды)",
        help_text="Как часто читать данные"
    )
    
    enabled = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Включить/выключить опрос этого подключения"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Дополнительная информация"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Modbus подключение"
        verbose_name_plural = "Modbus подключения"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"


class ModbusRegisterMap(models.Model):
    """
    Mapping Modbus регистров к датчикам системы
    """
    REGISTER_TYPE_CHOICES = [
        ('holding', 'Holding Register (40001+)'),
        ('input', 'Input Register (30001+)'),
        ('coil', 'Coil (00001+)'),
        ('discrete', 'Discrete Input (10001+)'),
    ]
    
    DATA_TYPE_CHOICES = [
        ('int16', 'Int16 (signed)'),
        ('uint16', 'UInt16 (unsigned)'),
        ('int32', 'Int32 (2 registers)'),
        ('uint32', 'UInt32 (2 registers)'),
        ('float32', 'Float32 (2 registers)'),
        ('bool', 'Boolean'),
    ]
    
    connection = models.ForeignKey(
        ModbusConnection,
        on_delete=models.CASCADE,
        related_name='register_maps',
        verbose_name="Modbus подключение"
    )
    
    # Связь с датчиком (опционально, пока нет модели Sensor)
    # sensor = models.ForeignKey(
    #     'Atributes',  # Используем существующую модель
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='modbus_registers',
    #     verbose_name="Датчик",
    #     help_text="К какому датчику привязан этот регистр"
    # )
    
    # Временное решение: текстовое поле для имени датчика
    sensor_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Имя датчика",
        help_text="Название датчика/параметра"
    )
    
    register_type = models.CharField(
        max_length=20,
        choices=REGISTER_TYPE_CHOICES,
        verbose_name="Тип регистра"
    )
    
    address = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
        verbose_name="Адрес регистра",
        help_text="0-based адрес (например: 0 = 40001)"
    )
    
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='int16',
        verbose_name="Тип данных"
    )
    
    scale_factor = models.FloatField(
        default=1.0,
        verbose_name="Масштабный коэффициент",
        help_text="Умножить значение на этот коэффициент (например: 0.1 для деления на 10)"
    )
    
    offset = models.FloatField(
        default=0.0,
        verbose_name="Смещение",
        help_text="Добавить к значению после масштабирования"
    )
    
    enabled = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Modbus регистр"
        verbose_name_plural = "Modbus регистры"
        ordering = ['connection', 'address']
        unique_together = [['connection', 'register_type', 'address']]
    
    def __str__(self):
        return f"{self.connection.name} - {self.register_type}[{self.address}] -> {self.sensor.name}"
    
    def calculate_value(self, raw_value):
        """
        Преобразует сырое значение из Modbus в физическую величину
        """
        return (raw_value * self.scale_factor) + self.offset


class ModbusConnectionLog(models.Model):
    """
    Логи подключений и ошибок Modbus
    """
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
        ('timeout', 'Таймаут'),
    ]
    
    connection = models.ForeignKey(
        ModbusConnection,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name="Подключение"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Статус"
    )
    
    message = models.TextField(
        verbose_name="Сообщение"
    )
    
    registers_read = models.IntegerField(
        default=0,
        verbose_name="Прочитано регистров"
    )
    
    duration_ms = models.IntegerField(
        default=0,
        verbose_name="Длительность (мс)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Лог Modbus"
        verbose_name_plural = "Логи Modbus"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['connection', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.connection.name} - {self.status} ({self.created_at})"


class SensorData(models.Model):
    """
    Исторические данные с датчиков Modbus
    Phase 4.6: Enhanced Emulator v2.0 Integration
    """
    
    # Связи
    connection = models.ForeignKey(
        'ModbusConnection',
        on_delete=models.CASCADE,
        related_name='sensor_data',
        verbose_name="Modbus соединение"
    )
    
    register_map = models.ForeignKey(
        'ModbusRegisterMap',
        on_delete=models.CASCADE,
        related_name='sensor_data',
        verbose_name="Регистр"
    )
    
    sensor = models.ForeignKey(
        'Sensor',
        on_delete=models.CASCADE,
        related_name='modbus_data',
        verbose_name="Датчик"
    )
    
    # Данные
    raw_value = models.FloatField(
        verbose_name="Сырое значение",
        help_text="Значение напрямую из Modbus регистра"
    )
    
    calculated_value = models.FloatField(
        verbose_name="Рассчитанное значение",
        help_text="После применения scale_factor и offset"
    )
    
    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Единица измерения"
    )
    
    # Временная метка
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время получения",
        db_index=True
    )
    
    # Качество данных
    quality = models.CharField(
        max_length=20,
        choices=[
            ('good', 'Хорошее'),
            ('uncertain', 'Неопределённое'),
            ('bad', 'Плохое'),
        ],
        default='good',
        verbose_name="Качество данных"
    )
    
    class Meta:
        verbose_name = "Данные датчика Modbus"
        verbose_name_plural = "Данные датчиков Modbus"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['connection', '-timestamp']),
            models.Index(fields=['register_map', '-timestamp']),
        ]
        # Для оптимизации запросов за период
        db_table = 'data_sensordata'
    
    def __str__(self):
        return f"{self.sensor.name}: {self.calculated_value} {self.unit} ({self.timestamp})"
    
    def save(self, *args, **kwargs):
        """
        Автоматически рассчитывает calculated_value при сохранении
        """
        if self.register_map:
            self.calculated_value = self.register_map.calculate_value(self.raw_value)
            # Берём единицу измерения из датчика
            self.unit = self.sensor.unit if self.sensor else ''
        super().save(*args, **kwargs)
