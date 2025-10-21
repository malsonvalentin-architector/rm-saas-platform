"""
Emergency fix command to immediately update test users without redeploy.
Run this via: python manage.py fix_test_users_now
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'EMERGENCY: Fix test users credentials and company assignments NOW'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.WARNING('EMERGENCY FIX: Updating test users...'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')

        # Step 1: Get or create demo company
        demo_company, created = Company.objects.get_or_create(
            name='ProMonitor Demo',
            defaults={
                'address': 'Demo Address, Almaty, Kazakhstan',
                'contact_email': 'demo@promonitor.kz',
                'contact_phone': '+7 (777) 000-00-00',
                'subscription_status': 'active',
                'subscription_end_date': timezone.now().date() + timedelta(days=365),
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created demo company: {demo_company.name} (ID: {demo_company.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found existing demo company: {demo_company.name} (ID: {demo_company.id})'))

        self.stdout.write('')

        # Step 2: Fix admin@promonitor.kz password
        try:
            admin_user = User_profile.objects.get(email='admin@promonitor.kz')
            admin_user.set_password('Admin123!')
            admin_user.company = demo_company
            admin_user.role = 'admin'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ FIXED: admin@promonitor.kz | Password changed to Admin123! | Company: {demo_company.name}'
            ))
        except User_profile.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ admin@promonitor.kz not found!'))

        # Step 3: Fix manager@promonitor.kz
        try:
            manager_user = User_profile.objects.get(email='manager@promonitor.kz')
            manager_user.company = demo_company
            manager_user.role = 'manager'
            manager_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ FIXED: manager@promonitor.kz | Company: {demo_company.name} | Role: {manager_user.role}'
            ))
        except User_profile.DoesNotExist:
            # Create if doesn't exist
            manager_user = User_profile.objects.create(
                email='manager@promonitor.kz',
                username='manager',
                first_name='Manager',
                last_name='User',
                role='manager',
                company=demo_company,
                is_active=True
            )
            manager_user.set_password('Manager123!')
            manager_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ CREATED: manager@promonitor.kz | Password: Manager123! | Company: {demo_company.name}'
            ))

        # Step 4: Fix client@promonitor.kz
        try:
            client_user = User_profile.objects.get(email='client@promonitor.kz')
            client_user.company = demo_company
            client_user.role = 'client'
            client_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ FIXED: client@promonitor.kz | Company: {demo_company.name} | Role: {client_user.role}'
            ))
        except User_profile.DoesNotExist:
            # Create if doesn't exist
            client_user = User_profile.objects.create(
                email='client@promonitor.kz',
                username='client',
                first_name='Client',
                last_name='User',
                role='client',
                company=demo_company,
                is_active=True
            )
            client_user.set_password('Client123!')
            client_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ CREATED: client@promonitor.kz | Password: Client123! | Company: {demo_company.name}'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.SUCCESS('✓✓✓ EMERGENCY FIX COMPLETED! ✓✓✓'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')
        
        # Summary
        self.stdout.write(self.style.NOTICE('UPDATED CREDENTIALS:'))
        self.stdout.write(self.style.NOTICE('-' * 80))
        self.stdout.write(f'  admin@promonitor.kz    | Password: Admin123!    | Company: {demo_company.name}')
        self.stdout.write(f'  manager@promonitor.kz  | Password: Manager123!  | Company: {demo_company.name}')
        self.stdout.write(f'  client@promonitor.kz   | Password: Client123!   | Company: {demo_company.name}')
        self.stdout.write(self.style.NOTICE('-' * 80))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Try logging in now at https://www.promonitor.kz/login/'))
