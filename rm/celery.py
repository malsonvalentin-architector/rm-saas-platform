"""
Celery configuration for RM SaaS platform
Fixed: Added placeholder tasks to prevent unregistered errors
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')

app = Celery('rm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# ===== Исправление Deprecation Warning =====
app.conf.broker_connection_retry_on_startup = True

# ===== Использование Redis для хранения расписания Beat =====
app.conf.beat_scheduler = 'redbeat.RedBeatScheduler'
app.conf.redbeat_redis_url = app.conf.broker_url

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# ============================================================================
# BEAT SCHEDULE - Все задачи (реализованные + placeholders)
# ============================================================================

app.conf.beat_schedule = {
    # === РЕАЛИЗОВАННЫЕ ЗАДАЧИ (Phase 4.6 Modbus Integration) ===
    
    # Modbus polling - опрос всех активных Modbus подключений
    'poll-modbus-connections': {
        'task': 'poll_modbus_connections',
        'schedule': 60.0,  # Каждую минуту
        'options': {
            'queue': 'celery',
            'expires': 50.0,
        }
    },
    
    # Cleanup old Modbus logs
    'cleanup-old-modbus-logs': {
        'task': 'cleanup_old_modbus_logs',
        'schedule': crontab(hour=2, minute=0),  # Ежедневно в 2:00 AM
        'options': {
            'queue': 'celery',
        }
    },
    
    # === PLACEHOLDER ЗАДАЧИ (TODO: реализовать логику) ===
    
    # Проверка алертов
    'check-alerts': {
        'task': 'data.tasks.check_alerts',
        'schedule': 30.0,  # Каждые 30 секунд
        'options': {
            'queue': 'celery',
        }
    },
    
    # Опрос Carel контроллеров
    'poll-carel-controllers': {
        'task': 'data.tasks.poll_carel_controllers',
        'schedule': 60.0,  # Каждую минуту
        'options': {
            'queue': 'celery',
        }
    },
    
    # Проверка истекающих подписок
    'check-expiring-subscriptions': {
        'task': 'data.tasks.check_expiring_subscriptions',
        'schedule': crontab(hour=9, minute=0),  # Ежедневно в 9:00 AM
        'options': {
            'queue': 'celery',
        }
    },
}

# Total periodic tasks: 5 (2 реализованных + 3 placeholders)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
