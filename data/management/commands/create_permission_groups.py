"""
Management command для создания Django Groups для каждой роли.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from data.models import Company, Obj, System, Atributes, SubscriptionPlan, User_profile


class Command(BaseCommand):
    help = 'Create Django Groups for roles: superadmin, admin, manager, client'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Creating Permission Groups ===\n'))
        
        role_permissions = {
            'superadmin': {
                'description': 'Full system access - all permissions',
                'models': [User_profile, Company, Obj, System, Atributes, SubscriptionPlan],
                'permissions': ['add', 'change', 'delete', 'view'],
            },
            'admin': {
                'description': 'Company admin - manage own company',
                'models': [Obj, System, Atributes, User_profile],
                'permissions': ['add', 'change', 'delete', 'view'],
            },
            'manager': {
                'description': 'Manager - manage objects and sensors',
                'models': [Obj, System, Atributes],
                'permissions': ['add', 'change', 'view'],
            },
            'client': {
                'description': 'Client - read-only access',
                'models': [Obj, System, Atributes],
                'permissions': ['view'],
            },
        }
        
        for role_name, config in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Created group: {role_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'[SKIP] Group already exists: {role_name}'))
                group.permissions.clear()
            
            self.stdout.write(f'  Description: {config["description"]}')
            
            permission_count = 0
            for model in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                
                for perm_type in config['permissions']:
                    codename = f'{perm_type}_{model._meta.model_name}'
                    
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        group.permissions.add(permission)
                        permission_count += 1
                        
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f'  [ERROR] Permission not found: {codename}')
                        )
            
            self.stdout.write(self.style.SUCCESS(f'  [OK] Added {permission_count} permissions\n'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Permission Groups Created Successfully ===\n'))
        
        self.stdout.write(self.style.SUCCESS('Summary:'))
        for role_name in role_permissions.keys():
            group = Group.objects.get(name=role_name)
            perm_count = group.permissions.count()
            self.stdout.write(f'  {role_name}: {perm_count} permissions')
