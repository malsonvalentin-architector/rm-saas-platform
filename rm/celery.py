"""
Celery configuration for RM SaaS platform
Fixed: Removed non-existent tasks from beat_schedule
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
# BEAT SCHEDULE - ТОЛЬКО СУЩЕСТВУЮЩИЕ ЗАДАЧИ (Phase 4.6 Modbus Integration)
# ============================================================================

app.conf.beat_schedule = {
    # Modbus polling - опрос всех активных Modbus подключений
    'poll-modbus-connections': {
        'task': 'poll_modbus_connections',
        'schedule': 60.0,  # Каждую минуту
        'options': {
            'queue': 'celery',
            'expires': 50.0,  # Задача истекает через 50 сек
        }
    },
    
    # Cleanup old Modbus logs - очистка старых логов
    'cleanup-old-modbus-logs': {
        'task': 'cleanup_old_modbus_logs',
        'schedule': crontab(hour=2, minute=0),  # Каждый день в 2:00 AM
        'options': {
            'queue': 'celery',
        }
    },
}

# Total periodic tasks: 2 (ТОЛЬКО проверенные существующие задачи)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
