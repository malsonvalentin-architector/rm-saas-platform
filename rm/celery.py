"""
Celery configuration for RM SaaS platform
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')

app = Celery('rm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print('Request: {0!r}'.format(self.request))

# ============================================================================
# HARDCODED BEAT SCHEDULE (No database dependency)
# ============================================================================

from celery.schedules import crontab

app.conf.beat_schedule = {
    # Polling tasks (high frequency)
    'poll-critical-sensors': {
        'task': 'data.tasks.poll_critical_sensors',
        'schedule': 30.0,  # Every 30 seconds
    },
    'poll-normal-sensors': {
        'task': 'data.tasks.poll_normal_sensors',
        'schedule': 60.0,  # Every minute
    },
    'poll-low-frequency-sensors': {
        'task': 'data.tasks.poll_low_frequency_sensors',
        'schedule': 300.0,  # Every 5 minutes
    },
    
    # Aggregation tasks
    'aggregate-hourly': {
        'task': 'data.tasks.aggregate_sensor_data',
        'schedule': crontab(minute=0),  # Every hour
        'kwargs': {'period': 'hourly'},
    },
    'aggregate-daily': {
        'task': 'data.tasks.aggregate_sensor_data',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
        'kwargs': {'period': 'daily'},
    },
    'aggregate-weekly': {
        'task': 'data.tasks.aggregate_sensor_data',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),  # Monday midnight
        'kwargs': {'period': 'weekly'},
    },
    
    # System maintenance
    'system-health-check': {
        'task': 'data.tasks.system_health_check',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-readings': {
        'task': 'data.tasks.cleanup_old_readings',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    
    # Analytics
    'detect-anomalies': {
        'task': 'data.tasks.detect_anomalies',
        'schedule': crontab(minute=15),  # Every hour at :15
    },
    'predictive-analytics': {
        'task': 'data.tasks.run_predictive_analytics',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
}

print("✅ Celery Beat configured successfully!")
print(f"📊 Total periodic tasks: {len(app.conf.beat_schedule)}")
