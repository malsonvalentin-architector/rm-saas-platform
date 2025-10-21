from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from data.models import Company, Object, Sensor, Alert, SubscriptionPlan, User_profile


class Command(BaseCommand):
    help = 'Create Django Groups for roles'

    def handle(self, *args, **options):
        role_permissions = {
            'superadmin': {
                'models': [User_profile, Company, Object, Sensor, Alert, SubscriptionPlan],
                'permissions': ['add', 'change', 'delete', 'view'],
            },
            'admin': {
                'models': [Object, Sensor, Alert, User_profile],
                'permissions': ['add', 'change', 'delete', 'view'],
            },
            'manager': {
                'models': [Object, Sensor, Alert],
                'permissions': ['add', 'change', 'view'],
            },
            'client': {
                'models': [Object, Sensor, Alert],
                'permissions': ['view'],
            },
        }
        
        for role_name, config in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if not created:
                group.permissions.clear()
            
            for model in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                for perm_type in config['permissions']:
                    codename = f'{perm_type}_{model._meta.model_name}'
                    try:
                        permission = Permission.objects.get(codename=codename, content_type=content_type)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass
            
            self.stdout.write(self.style.SUCCESS(f'[OK] {role_name}: {group.permissions.count()} permissions'))
