"""
Check current status of test users in database
"""
from django.core.management.base import BaseCommand
from data.models import User_profile, Company


class Command(BaseCommand):
    help = 'Check current status of test users'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('CHECKING TEST USERS STATUS')
        self.stdout.write('='*80)
        self.stdout.write('')

        # Check companies
        self.stdout.write('COMPANIES:')
        self.stdout.write('-'*80)
        companies = Company.objects.all()
        if not companies.exists():
            self.stdout.write('  ⚠️  NO COMPANIES FOUND!')
        else:
            for company in companies:
                self.stdout.write(f'  • {company.name} (ID: {company.id})')
        self.stdout.write('')

        # Check test users
        test_emails = [
            'admin@promonitor.kz',
            'manager@promonitor.kz',
            'client@promonitor.kz',
            'superadmin@test.kz'
        ]

        self.stdout.write('TEST USERS:')
        self.stdout.write('-'*80)
        
        for email in test_emails:
            try:
                user = User_profile.objects.get(email=email)
                company_name = user.company.name if user.company else 'NO COMPANY'
                self.stdout.write(
                    f'  ✓ {email:30} | Role: {user.role:10} | Company: {company_name}'
                )
            except User_profile.DoesNotExist:
                self.stdout.write(f'  ✗ {email:30} | NOT FOUND')

        self.stdout.write('')
        self.stdout.write('='*80)
