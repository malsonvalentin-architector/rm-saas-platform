"""
Setup default users for ProMonitor.kz
Creates superadmin and admin users with correct roles
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'Setup default superadmin and admin users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.WARNING('SETTING UP DEFAULT USERS'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')

        # Step 1: Create ProMonitor Admin company
        admin_company, created = Company.objects.get_or_create(
            name='ProMonitor Admin',
            defaults={
                'contact_person': 'Admin',
                'contact_email': 'admin@promonitor.kz',
                'subscription_status': 'active',
                'subscription_end_date': timezone.now().date() + timedelta(days=3650),  # 10 years
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created company: {admin_company.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found company: {admin_company.name}'))
        
        self.stdout.write('')

        # Step 2: Create/Update SUPERADMIN (superadmin@promonitor.kz)
        superadmin, created = User_profile.objects.update_or_create(
            email='superadmin@promonitor.kz',
            defaults={
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'superadmin',
                'company': None,  # Superadmin is not tied to any company
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        superadmin.set_password('Super123!')
        superadmin.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ CREATED: superadmin@promonitor.kz'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ UPDATED: superadmin@promonitor.kz'))
        
        self.stdout.write(f'  - Password: Super123!')
        self.stdout.write(f'  - Role: superadmin')
        self.stdout.write(f'  - Company: None (can see all companies)')
        self.stdout.write(f'  - is_superuser: True')
        self.stdout.write('')

        # Step 3: Create/Update ADMIN (admin@promonitor.kz)
        admin, created = User_profile.objects.update_or_create(
            email='admin@promonitor.kz',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',  # ВАЖНО: admin, не superadmin!
                'company': admin_company,
                'is_staff': True,
                'is_superuser': False,  # Admin is NOT superuser
                'is_active': True,
            }
        )
        admin.set_password('Vika2025')
        admin.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ CREATED: admin@promonitor.kz'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ UPDATED: admin@promonitor.kz'))
        
        self.stdout.write(f'  - Password: Vika2025')
        self.stdout.write(f'  - Role: admin')
        self.stdout.write(f'  - Company: {admin_company.name}')
        self.stdout.write(f'  - is_superuser: False')
        self.stdout.write('')

        # Summary
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.SUCCESS('✅ DEFAULT USERS SETUP COMPLETED!'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')
        
        self.stdout.write(self.style.NOTICE('CREDENTIALS:'))
        self.stdout.write(self.style.NOTICE('-'*80))
        self.stdout.write('  SUPERADMIN:')
        self.stdout.write('    Email:    superadmin@promonitor.kz')
        self.stdout.write('    Password: Super123!')
        self.stdout.write('    Role:     superadmin (sees ALL companies)')
        self.stdout.write('')
        self.stdout.write('  ADMIN:')
        self.stdout.write('    Email:    admin@promonitor.kz')
        self.stdout.write('    Password: Vika2025')
        self.stdout.write('    Role:     admin (Company Administrator)')
        self.stdout.write('    Company:  ProMonitor Admin')
        self.stdout.write(self.style.NOTICE('-'*80))
        self.stdout.write('')
