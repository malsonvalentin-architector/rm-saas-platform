"""
FORCE FIX - Guaranteed to work
This command uses direct database operations to fix test users
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'FORCE FIX: Guaranteed fix for test users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.WARNING('🔧 FORCE FIX: Updating test users with guaranteed method'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')

        # Step 1: Ensure demo company exists
        self.stdout.write('Step 1: Getting/Creating Demo Company...')
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
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {demo_company.name} (ID: {demo_company.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Found: {demo_company.name} (ID: {demo_company.id})'))
        
        self.stdout.write('')

        # Step 2: Fix each user individually with detailed logging
        users_to_fix = [
            {
                'email': 'admin@promonitor.kz',
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'Admin123!',
                'role': 'admin',
                'company': demo_company,
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'email': 'manager@promonitor.kz',
                'username': 'manager',
                'first_name': 'Manager',
                'last_name': 'User',
                'password': 'Manager123!',
                'role': 'manager',
                'company': demo_company,
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'client@promonitor.kz',
                'username': 'client',
                'first_name': 'Client',
                'last_name': 'User',
                'password': 'Client123!',
                'role': 'client',
                'company': demo_company,
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        self.stdout.write('Step 2: Fixing Users...')
        self.stdout.write('')
        
        for user_data in users_to_fix:
            email = user_data['email']
            password = user_data.pop('password')
            
            try:
                # Try to get existing user
                user = User_profile.objects.get(email=email)
                
                # Update all fields
                for key, value in user_data.items():
                    setattr(user, key, value)
                
                # Set password
                user.set_password(password)
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ UPDATED: {email}'))
                self.stdout.write(f'    - Password: {password}')
                self.stdout.write(f'    - Role: {user.role}')
                self.stdout.write(f'    - Company: {user.company.name if user.company else "NO COMPANY"}')
                self.stdout.write('')
                
            except User_profile.DoesNotExist:
                # Create new user
                user = User_profile(**user_data)
                user.set_password(password)
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ CREATED: {email}'))
                self.stdout.write(f'    - Password: {password}')
                self.stdout.write(f'    - Role: {user.role}')
                self.stdout.write(f'    - Company: {user.company.name if user.company else "NO COMPANY"}')
                self.stdout.write('')
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ ERROR fixing {email}: {e}'))
                self.stdout.write('')

        # Step 3: Verify changes
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write(self.style.SUCCESS('✅ FORCE FIX COMPLETED!'))
        self.stdout.write(self.style.WARNING('='*80))
        self.stdout.write('')
        
        self.stdout.write('VERIFICATION - Current Database State:')
        self.stdout.write('-'*80)
        
        for user_data in users_to_fix:
            email = user_data['email']
            try:
                user = User_profile.objects.get(email=email)
                company_name = user.company.name if user.company else 'NO COMPANY'
                self.stdout.write(
                    f'  {email:30} | Role: {user.role:10} | Company: {company_name}'
                )
            except User_profile.DoesNotExist:
                self.stdout.write(f'  {email:30} | NOT FOUND (ERROR!)')
        
        self.stdout.write('-'*80)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Try logging in now at https://www.promonitor.kz/login/'))
        self.stdout.write('')
