"""
Celery configuration for RM SaaS platform
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

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# ============================================================================
# HARDCODED BEAT SCHEDULE (Using REAL tasks from data/tasks.py)
# ============================================================================

app.conf.beat_schedule = {
    # Polling Carel controllers (main polling task)
    'poll-carel-controllers': {
        'task': 'data.tasks.poll_carel_controllers',
        'schedule': 60.0,  # Every minute
    },
    
    # Alert checking
    'check-alerts': {
        'task': 'data.tasks.check_alerts',
        'schedule': 30.0,  # Every 30 seconds
    },
    
    # Subscription management
    'check-expiring-subscriptions': {
        'task': 'data.tasks.check_expiring_subscriptions',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}

# Celery Beat schedule configured above
# Total periodic tasks: 3


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print('Request: {0!r}'.format(self.request))
