# Generated manually for subscription system v2

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_create_subscription_plans'),
    ]

    operations = [
        # Удаляем старые модели
        migrations.DeleteModel(
            name='Invoice',
        ),
        
        # Создаём новые модели
        migrations.CreateModel(
            name='AddonModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_type', models.CharField(choices=[('ai_assistant', '🤖 AI Chat Assistant'), ('predictive', '🔮 Predictive Analytics'), ('optimization', '⚡ Autonomous Optimization')], max_length=20, verbose_name='Тип модуля')),
                ('tier', models.CharField(choices=[('starter', 'Starter'), ('basic', 'Basic'), ('professional', 'Professional'), ('pro', 'Pro'), ('enterprise', 'Enterprise')], max_length=20, verbose_name='Уровень')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена в месяц ($)')),
                ('ai_requests_limit', models.IntegerField(blank=True, help_text='NULL = безлимит', null=True, verbose_name='Лимит AI запросов/месяц')),
                ('prediction_accuracy', models.IntegerField(blank=True, null=True, verbose_name='Точность предсказаний (%)')),
                ('prediction_days', models.IntegerField(blank=True, null=True, verbose_name='Горизонт прогноза (дней)')),
                ('energy_saving_min', models.IntegerField(blank=True, null=True, verbose_name='Минимальная экономия (%)')),
                ('energy_saving_max', models.IntegerField(blank=True, null=True, verbose_name='Максимальная экономия (%)')),
                ('automation_level', models.CharField(blank=True, help_text='Recommendations / Semi-autonomous / Fully autonomous', max_length=50, verbose_name='Уровень автоматизации')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_coming_soon', models.BooleanField(default=False, verbose_name='Coming Soon')),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Дополнительный модуль',
                'verbose_name_plural': 'Дополнительные модули',
                'ordering': ['module_type', 'sort_order'],
            },
        ),
        
        # Обновляем SubscriptionPlan
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='has_email_notifications',
        ),
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='has_telegram_notifications',
        ),
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='is_public',
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='has_sla',
            field=models.BooleanField(default=False, verbose_name='SLA 99.9%'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='is_featured',
            field=models.BooleanField(default=False, verbose_name='Рекомендуемый'),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='price_yearly',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='При годовой оплате (обычно со скидкой 20%)', max_digits=10, null=True, verbose_name='Цена в год ($)'),
        ),
        
        # Обновляем Subscription
        migrations.RemoveField(
            model_name='subscription',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='auto_renew',
        ),
        migrations.AddField(
            model_name='subscription',
            name='addon_modules',
            field=models.ManyToManyField(blank=True, to='data.addonmodule', verbose_name='Дополнительные модули'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='base_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Цена базового тарифа', max_digits=10, verbose_name='Базовая цена ($)'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='addons_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Сумма всех дополнительных модулей', max_digits=10, verbose_name='Цена модулей ($)'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Базовая цена + модули', max_digits=10, verbose_name='Итоговая цена ($)'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('trial', 'Пробный период'), ('active', 'Активна'), ('past_due', 'Просрочен платёж'), ('cancelled', 'Отменена'), ('expired', 'Истекла')], default='trial', max_length=20, verbose_name='Статус'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='trial_ends_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Окончание trial'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='current_period_start',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Начало периода'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='current_period_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Конец периода'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='paid_until',
            field=models.DateTimeField(blank=True, help_text='Админ устанавливает вручную', null=True, verbose_name='Оплачено до'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Заметки админа'),
        ),
        
        # Создаём модель Payment
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма ($)')),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('completed', 'Оплачен'), ('failed', 'Ошибка'), ('refunded', 'Возврат')], default='pending', max_length=20, verbose_name='Статус')),
                ('payment_method', models.CharField(blank=True, help_text='Kaspi, Банковский перевод, и т.д.', max_length=50, verbose_name='Способ оплаты')),
                ('transaction_id', models.CharField(blank=True, max_length=200, verbose_name='ID транзакции')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата оплаты')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='data.subscription', verbose_name='Подписка')),
            ],
            options={
                'verbose_name': 'Платёж',
                'verbose_name_plural': 'Платежи',
                'ordering': ['-created_at'],
            },
        ),
        
        # Добавляем unique constraint для AddonModule
        migrations.AddConstraint(
            model_name='addonmodule',
            constraint=models.UniqueConstraint(fields=('module_type', 'tier'), name='unique_module_tier'),
        ),
    ]
