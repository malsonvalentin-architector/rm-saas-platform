"""
МОДЕЛИ ДЛЯ SaaS ПЛАТФОРМЫ
Версия 2.0 с Multi-Tenancy и подписками
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


# ============================================================================
# МОДЕЛИ ПОДПИСОК
# ============================================================================

class SubscriptionPlan(models.Model):
    """Тарифный план"""
    
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Код")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Цена
    price_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена в месяц (USD)"
    )
    price_yearly = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена в год (USD)"
    )
    
    # Лимиты
    max_objects = models.IntegerField(default=5, verbose_name="Макс. объектов")
    max_systems = models.IntegerField(default=10, verbose_name="Макс. систем")
    max_users = models.IntegerField(default=5, verbose_name="Макс. пользователей")
    max_data_retention_days = models.IntegerField(default=30, verbose_name="Хранение данных (дней)")
    
    # Возможности
    has_api_access = models.BooleanField(default=False, verbose_name="Доступ к API")
    has_telegram_notifications = models.BooleanField(default=False, verbose_name="Telegram уведомления")
    has_email_notifications = models.BooleanField(default=True, verbose_name="Email уведомления")
    has_custom_reports = models.BooleanField(default=False, verbose_name="Кастомные отчеты")
    has_white_label = models.BooleanField(default=False, verbose_name="White-label")
    has_priority_support = models.BooleanField(default=False, verbose_name="Приоритетная поддержка")
    
    # Системные поля
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_public = models.BooleanField(default=True, verbose_name="Показывать на сайте")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    
    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"
        ordering = ['sort_order', 'price_monthly']
    
    def __str__(self):
        return f"{self.name} (${self.price_monthly}/мес)"
    
    def get_yearly_savings(self):
        """Экономия при годовой оплате"""
        monthly_total = self.price_monthly * 12
        return monthly_total - self.price_yearly


class Subscription(models.Model):
    """Подписка компании"""
    
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="Компания"
    )
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        verbose_name="Тарифный план"
    )
    
    # Период
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    billing_period = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Ежемесячно'),
            ('yearly', 'Ежегодно'),
        ],
        default='monthly',
        verbose_name="Период оплаты"
    )
    
    # Оплата
    is_paid = models.BooleanField(default=False, verbose_name="Оплачена")
    auto_renew = models.BooleanField(default=True, verbose_name="Автопродление")
    
    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Отменена")
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"
    
    def is_active(self):
        """Активна ли подписка"""
        return (
            self.is_paid and 
            self.start_date <= timezone.now().date() <= self.end_date and
            not self.cancelled_at
        )
    
    def days_until_expiration(self):
        """Дней до истечения"""
        delta = self.end_date - timezone.now().date()
        return delta.days if delta.days > 0 else 0


class Invoice(models.Model):
    """Счет на оплату"""
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="Компания"
    )
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Подписка"
    )
    
    # Номер счета (генерируется автоматически)
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Номер счета")
    
    # Сумма
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency = models.CharField(max_length=3, default='USD', verbose_name="Валюта")
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Черновик'),
            ('pending', 'Ожидает оплаты'),
            ('paid', 'Оплачен'),
            ('cancelled', 'Отменен'),
            ('failed', 'Ошибка оплаты'),
            ('refunded', 'Возврат'),
        ],
        default='pending',
        verbose_name="Статус"
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Оплачен")
    due_date = models.DateField(verbose_name="Срок оплаты")
    
    # Дополнительно
    description = models.TextField(blank=True, verbose_name="Описание")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Способ оплаты")
    
    class Meta:
        verbose_name = "Счет"
        verbose_name_plural = "Счета"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['company', 'status']),
        ]
    
    def __str__(self):
        return f"Счет {self.invoice_number} - {self.company.name}"
    
    def save(self, *args, **kwargs):
        # Автоматическая генерация номера счета
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[1])
                    self.invoice_number = f"INV-{last_number + 1:06d}"
                except:
                    self.invoice_number = f"INV-{self.id:06d}" if self.id else "INV-000001"
            else:
                self.invoice_number = "INV-000001"
        super().save(*args, **kwargs)


# ============================================================================
# ОБНОВЛЕННЫЕ МОДЕЛИ С ПРИВЯЗКОЙ К КОМПАНИИ
# ============================================================================

class User_profile(AbstractUser):
    """Пользователь с поддержкой Multi-Tenancy"""
    
    username = None
    email = models.EmailField("Email Address", unique=True)
    phone_number = PhoneNumberField(blank=True, verbose_name="Телефон")
    
    # НОВОЕ: Привязка к компании
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,  # Временно для миграции
        blank=True,
        verbose_name="Компания"
    )
    
    # НОВОЕ: Роль пользователя
    role = models.CharField(
        max_length=20,
        choices=[
            ('company_admin', 'Администратор компании'),
            ('operator', 'Оператор'),
            ('viewer', 'Наблюдатель'),
        ],
        default='operator',
        verbose_name="Роль"
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
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['company', 'email']
    
    def __str__(self):
        company_name = self.company.name if self.company else 'Без компании'
        return f"{self.email} ({company_name})"
    
    def can_manage_company(self):
        """Может ли управлять компанией"""
        return self.role == 'company_admin' or self.is_superuser
    
    def can_control_equipment(self):
        """Может ли управлять оборудованием"""
        return self.role in ['company_admin', 'operator'] or self.is_superuser
    
    def can_view_only(self):
        """Только просмотр"""
        return self.role == 'viewer'


class Obj(models.Model):
    """Объект (здание, помещение) - ОБНОВЛЕННАЯ ВЕРСИЯ"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    obj = models.CharField(max_length=200, verbose_name="Название объекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # ИЗМЕНЕНО: Привязка к компании вместо пользователя
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания"
    )
    
    # Дополнительная информация
    address = models.CharField(max_length=300, blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
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
        return f'{self.obj} ({self.company.name})'


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
    recipients = models.JSONField(default=list, blank=True, verbose_name="Получатели")
    
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

