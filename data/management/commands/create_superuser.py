from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.models import Company

class Command(BaseCommand):
    help = 'Create superuser with email login'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if superuser exists
        if User.objects.filter(email='admin@example.com').exists():
            self.stdout.write(self.style.WARNING('Superuser already exists: admin@example.com'))
            return
        
        # Create default company if not exists
        company, created = Company.objects.get_or_create(
            name='Default Company',
            defaults={
                'contact_person': 'Admin',
                'contact_email': 'admin@example.com',
                'subscription_status': 'trial'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default company: {company.name}'))
        
        # Create superuser
        try:
            user = User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                company=company,
                role='company_admin'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser created successfully!'))
            self.stdout.write(self.style.SUCCESS('  Email: admin@example.com'))
            self.stdout.write(self.style.SUCCESS('  Password: admin123'))
            self.stdout.write(self.style.SUCCESS(f'  Company: {company.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating superuser: {e}'))
