"""
Management command to setup test users with proper company assignments.
This command creates/updates test users for all roles with correct credentials.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'Setup test users with proper company assignments for all roles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Setting up test users...'))

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
            self.stdout.write(self.style.SUCCESS(f'✓ Created demo company: {demo_company.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Using existing demo company: {demo_company.name}'))

        # Step 2: Define test users configuration
        test_users = [
            {
                'email': 'superadmin@test.kz',
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'password': 'SuperAdmin123!',
                'role': 'superadmin',
                'is_staff': True,
                'is_superuser': True,
                'company': None,  # Superadmin не привязан к компании
                'description': 'SuperAdmin (no company)'
            },
            {
                'email': 'admin@promonitor.kz',
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'Admin123!',  # Изменён с ProMonitor2025!
                'role': 'admin',
                'is_staff': True,
                'is_superuser': False,
                'company': demo_company,
                'description': 'Company Admin'
            },
            {
                'email': 'manager@promonitor.kz',
                'username': 'manager',
                'first_name': 'Manager',
                'last_name': 'User',
                'password': 'Manager123!',
                'role': 'manager',
                'is_staff': False,
                'is_superuser': False,
                'company': demo_company,
                'description': 'Manager'
            },
            {
                'email': 'client@promonitor.kz',
                'username': 'client',
                'first_name': 'Client',
                'last_name': 'User',
                'password': 'Client123!',
                'role': 'client',
                'is_staff': False,
                'is_superuser': False,
                'company': demo_company,
                'description': 'Client (read-only)'
            }
        ]

        # Step 3: Create or update each test user
        for user_data in test_users:
            email = user_data['email']
            password = user_data.pop('password')
            description = user_data.pop('description')
            
            user, created = User_profile.objects.update_or_create(
                email=email,
                defaults=user_data
            )
            
            # Set password (only if user was created or we want to reset it)
            user.set_password(password)
            user.save()
            
            status = 'Created' if created else 'Updated'
            company_name = user.company.name if user.company else 'No Company'
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {status}: {email} | Role: {user.role} | Company: {company_name} | {description}'
                )
            )

        # Step 4: Summary
        self.stdout.write(self.style.NOTICE('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('TEST USERS CREDENTIALS:'))
        self.stdout.write(self.style.NOTICE('='*80))
        
        credentials = [
            ('superadmin@test.kz', 'SuperAdmin123!', 'superadmin', 'No Company'),
            ('admin@promonitor.kz', 'Admin123!', 'admin', demo_company.name),
            ('manager@promonitor.kz', 'Manager123!', 'manager', demo_company.name),
            ('client@promonitor.kz', 'Client123!', 'client', demo_company.name),
        ]
        
        for email, pwd, role, company in credentials:
            self.stdout.write(
                f'  Email: {email:30} | Password: {pwd:20} | Role: {role:10} | Company: {company}'
            )
        
        self.stdout.write(self.style.NOTICE('='*80))
        self.stdout.write(self.style.SUCCESS('\n✓ All test users setup completed successfully!'))
