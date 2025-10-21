"""
Fix admin@promonitor.kz role from superadmin to admin
"""
from django.core.management.base import BaseCommand
from data.models import User_profile


class Command(BaseCommand):
    help = 'Fix admin@promonitor.kz role to be admin (not superadmin)'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('FIXING admin@promonitor.kz ROLE')
        self.stdout.write('='*80)
        self.stdout.write('')

        try:
            # Get admin@promonitor.kz
            user = User_profile.objects.get(email='admin@promonitor.kz')
            
            self.stdout.write(f'Current state:')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Role: {user.role}')
            self.stdout.write(f'  is_staff: {user.is_staff}')
            self.stdout.write(f'  is_superuser: {user.is_superuser}')
            self.stdout.write(f'  Company: {user.company.name if user.company else "None"}')
            self.stdout.write('')
            
            # Fix the role
            if user.role == 'superadmin':
                user.role = 'admin'
                user.is_superuser = False  # Admin is not superuser
                user.is_staff = True       # Admin can access Django admin
                user.save()
                
                self.stdout.write(self.style.SUCCESS('✓ FIXED!'))
                self.stdout.write('')
                self.stdout.write(f'New state:')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Role: {user.role}')
                self.stdout.write(f'  is_staff: {user.is_staff}')
                self.stdout.write(f'  is_superuser: {user.is_superuser}')
                self.stdout.write(f'  Company: {user.company.name if user.company else "None"}')
            else:
                self.stdout.write(self.style.WARNING(f'Role is already "{user.role}" - no changes needed'))
            
        except User_profile.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ admin@promonitor.kz not found!'))
        
        self.stdout.write('')
        self.stdout.write('='*80)
        self.stdout.write(self.style.SUCCESS('DONE!'))
        self.stdout.write('='*80)
