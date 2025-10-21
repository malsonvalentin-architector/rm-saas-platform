# Generated manually to fix subscription field changes
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_update_user_roles'),
    ]

    operations = [
        # Fix AddonModule constraint
        migrations.RemoveConstraint(
            model_name='addonmodule',
            name='unique_module_tier',
        ),
        migrations.AlterUniqueTogether(
            name='addonmodule',
            unique_together={('module_type', 'tier')},
        ),
        
        # Fix SubscriptionPlan fields (ensure proper defaults)
        migrations.AlterField(
            model_name='subscriptionplan',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Ensure Subscription fields are correct
        migrations.AlterField(
            model_name='subscription',
            name='company',
            field=models.OneToOneField(
                on_delete=models.CASCADE,
                to='data.company',
                verbose_name='Компания'
            ),
        ),
    ]
