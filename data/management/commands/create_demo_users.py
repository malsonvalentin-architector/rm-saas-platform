"""
Django management command to create demo users for ProMonitor
Usage: python manage.py create_demo_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'Create demo users with specified credentials'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo users...'))
        
        # Get or create ProMonitor company
        company, _ = Company.objects.get_or_create(
            name='ProMonitor Demo',
            defaults={
                'address': 'Almaty, Kazakhstan',
                'phone': '+7 (727) 000-00-00'
            }
        )
        
        users_to_create = [
            {
                'email': 'superadmin@promonitor.kz',
                'password': 'Super123!',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'company_admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'admin@promonitor.kz',
                'password': 'Vika2025',
                'first_name': 'Vika',
                'last_name': 'Administrator',
                'role': 'company_admin',
                'is_staff': True,
            },
            {
                'email': 'manager@promonitor.kz',
                'password': 'Vika2025',
                'first_name': 'Vika',
                'last_name': 'Manager',
                'role': 'operator',
            },
            {
                'email': 'client@promonitor.kz',
                'password': 'Client123!',
                'first_name': 'Client',
                'last_name': 'User',
                'role': 'viewer',
            },
        ]
        
        for user_data in users_to_create:
            email = user_data['email']
            password = user_data.pop('password')
            
            # Check if user already exists
            if User_profile.objects.filter(email=email).exists():
                user = User_profile.objects.get(email=email)
                # Update password
                user.password = make_password(password)
                user.save()
                self.stdout.write(
                    self.style.WARNING(f'✓ Updated password for: {email}')
                )
            else:
                # Create new user
                user = User_profile.objects.create(
                    company=company,
                    password=make_password(password),
                    is_active=True,
                    **user_data
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created user: {email}')
                )
            
            # Display credentials
            self.stdout.write(
                self.style.SUCCESS(
                    f'  → Email: {email} | Password: {password} | Role: {user.role}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ All demo users created/updated successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Company: {company.name}\n')
        )
