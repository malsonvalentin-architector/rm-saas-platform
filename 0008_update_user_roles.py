from django.db import migrations, models


def migrate_old_roles(apps, schema_editor):
    User_profile = apps.get_model('data', 'User_profile')
    role_mapping = {
        'company_admin': 'admin',
        'operator': 'manager',
        'viewer': 'client',
    }
    for user in User_profile.objects.all():
        if user.role in role_mapping:
            user.role = role_mapping[user.role]
            user.save()


def reverse_migrate_roles(apps, schema_editor):
    User_profile = apps.get_model('data', 'User_profile')
    reverse_mapping = {
        'admin': 'company_admin',
        'manager': 'operator',
        'client': 'viewer',
    }
    for user in User_profile.objects.all():
        if user.role in reverse_mapping:
            user.role = reverse_mapping[user.role]
            user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0007_subscriptionplan_subscriptionusage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile',
            name='role',
            field=models.CharField(
                choices=[
                    ('superadmin', 'Superadmin'),
                    ('admin', 'Company Admin'),
                    ('manager', 'Manager'),
                    ('client', 'Client')
                ],
                default='client',
                max_length=20
            ),
        ),
        migrations.RunPython(migrate_old_roles, reverse_migrate_roles),
    ]
