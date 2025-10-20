"""
Celery Tasks для RM SaaS Platform
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import requests

from .models import Company, Subscription, System, Atributes, Data, AlertRule


@shared_task
def check_expiring_subscriptions():
    """
    Проверка истекающих подписок и отправка уведомлений
    Запускается раз в день
    """
    expiring_soon = Company.objects.filter(
        subscription_expires_at__lte=timezone.now() + timedelta(days=7),
        subscription_expires_at__gte=timezone.now(),
        subscription_status='active'
    )
    
    for company in expiring_soon:
        days_left = (company.subscription_expires_at - timezone.now()).days
        
        # Отправка email администратору компании
        admin_users = company.users.filter(role='company_admin')
        for admin in admin_users:
            if admin.user.email:
                send_mail(
                    subject=f'Подписка истекает через {days_left} дней',
                    message=f'''
Здравствуйте, {admin.user.first_name}!

Подписка вашей компании "{company.name}" истекает {company.subscription_expires_at.strftime("%d.%m.%Y")}.

Осталось дней: {days_left}

Пожалуйста, продлите подписку, чтобы продолжить использование системы.

С уважением,
Команда RM SaaS
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.user.email],
                    fail_silently=False,
                )
    
    return f'Checked {expiring_soon.count()} expiring subscriptions'


@shared_task
def poll_carel_controllers():
    """
    Опрос всех активных CAREL контроллеров
    Запускается каждые 5 минут
    """
    # Получаем все активные системы от активных компаний
    active_systems = System.objects.filter(
        obj__company__enabled=True,
        obj__company__subscription_status='active',
        enabled=True
    )
    
    polled_count = 0
    error_count = 0
    
    for system in active_systems:
        try:
            # Получаем все атрибуты системы
            attributes = Atributes.objects.filter(sys=system)
            
            for attr in attributes:
                # Формируем URL для опроса
                url = f"http://{system.ip}/xxxx/getvarjson.cgi"
                params = {'var': attr.addr}
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    value = data.get('val', 0)
                    
                    # Сохраняем данные
                    Data.objects.create(
                        name=attr,
                        val=value,
                        date=timezone.now()
                    )
                    
                    polled_count += 1
                    
                    # Обновляем статус системы
                    system.is_online = True
                    system.last_poll_time = timezone.now()
                    system.save()
                else:
                    error_count += 1
                    
        except Exception as e:
            error_count += 1
            system.is_online = False
            system.save()
    
    return f'Polled {polled_count} attributes, {error_count} errors'


@shared_task
def check_alerts():
    """
    Проверка правил тревог и отправка уведомлений
    Запускается каждую минуту
    """
    active_rules = AlertRule.objects.filter(
        enabled=True,
        company__enabled=True,
        company__subscription_status='active'
    )
    
    alerts_triggered = 0
    
    for rule in active_rules:
        # Получаем последнее значение атрибута
        latest_data = Data.objects.filter(
            name=rule.attribute
        ).order_by('-date').first()
        
        if not latest_data:
            continue
        
        # Проверяем условие
        triggered = False
        if rule.condition == 'greater':
            triggered = latest_data.val > rule.threshold_value
        elif rule.condition == 'less':
            triggered = latest_data.val < rule.threshold_value
        elif rule.condition == 'equal':
            triggered = latest_data.val == rule.threshold_value
        
        if triggered:
            alerts_triggered += 1
            
            # Отправка email
            send_alert_email.delay(rule.id, latest_data.val)
            
            # Отправка в Telegram (если настроен)
            if rule.company.current_subscription.plan.has_telegram:
                send_alert_telegram.delay(rule.id, latest_data.val)
    
    return f'Checked {active_rules.count()} rules, {alerts_triggered} alerts triggered'


@shared_task
def send_alert_email(rule_id, value):
    """Отправка email уведомления о тревоге"""
    try:
        rule = AlertRule.objects.get(id=rule_id)
        
        # Получаем администраторов компании
        admins = rule.company.users.filter(role='company_admin')
        
        for admin in admins:
            if admin.user.email:
                send_mail(
                    subject=f'⚠️ Тревога: {rule.alert_name}',
                    message=f'''
Внимание! Сработала тревога!

Компания: {rule.company.name}
Тревога: {rule.alert_name}
Система: {rule.attribute.sys.name}
Параметр: {rule.attribute.full_addr} ({rule.attribute.note})
Текущее значение: {value}
Порог: {rule.threshold_value}
Условие: {rule.get_condition_display()}

Описание: {rule.description}

Время: {timezone.now().strftime("%d.%m.%Y %H:%M:%S")}

---
RM SaaS Platform
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.user.email],
                    fail_silently=False,
                )
    except Exception as e:
        print(f'Error sending alert email: {e}')


@shared_task
def send_alert_telegram(rule_id, value):
    """Отправка Telegram уведомления о тревоге"""
    try:
        rule = AlertRule.objects.get(id=rule_id)
        
        # TODO: Implement Telegram notification
        # Здесь будет код для отправки в Telegram
        
        message = f'''
⚠️ **ТРЕВОГА**: {rule.alert_name}

🏢 Компания: {rule.company.name}
🖥 Система: {rule.attribute.sys.name}
📊 Параметр: {rule.attribute.note}
💯 Значение: {value} (порог: {rule.threshold_value})

📝 {rule.description}
        '''
        
        # Send to Telegram bot
        # bot.send_message(chat_id=rule.company.telegram_chat_id, text=message)
        
    except Exception as e:
        print(f'Error sending Telegram alert: {e}')


@shared_task
def send_welcome_email(user_id):
    """Отправка приветственного email новому пользователю"""
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.user_profile
        
        send_mail(
            subject='Добро пожаловать в RM SaaS!',
            message=f'''
Здравствуйте, {user.first_name}!

Добро пожаловать в систему мониторинга RM SaaS!

Ваша компания: {profile.company.name}
Ваша роль: {profile.get_role_display()}

Вы можете войти в систему по адресу:
https://{settings.ALLOWED_HOSTS[0]}/

Если у вас есть вопросы, свяжитесь с нами по адресу: {settings.ADMIN_EMAIL}

С уважением,
Команда RM SaaS
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f'Error sending welcome email: {e}')


@shared_task
def generate_invoice_pdf(invoice_id):
    """Генерация PDF счёта"""
    # TODO: Implement PDF generation
    pass
