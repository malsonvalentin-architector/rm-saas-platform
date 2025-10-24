# Generated migration for AI Assistant interaction logging

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0100_add_theme_dashboard_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIInteractionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=50, verbose_name='Session ID')),
                ('message', models.TextField(verbose_name='User Message')),
                ('response', models.TextField(verbose_name='AI Response')),
                ('intent', models.CharField(max_length=50, verbose_name='Detected Intent')),
                ('confidence', models.FloatField(default=0.0, verbose_name='Response Confidence')),
                ('context_data', models.JSONField(blank=True, default=dict, verbose_name='Context Data')),
                ('response_data', models.JSONField(blank=True, default=dict, verbose_name='Full Response Data')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'AI Interaction Log',
                'verbose_name_plural': 'AI Interaction Logs',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['user', '-timestamp'], name='ai_log_user_timestamp'),
                    models.Index(fields=['session_id', '-timestamp'], name='ai_log_session_timestamp'),
                    models.Index(fields=['intent', '-timestamp'], name='ai_log_intent_timestamp'),
                ],
            },
        ),
    ]