from django.core.management.base import BaseCommand
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Check if Django app can start properly'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('✓ Django imports successful'))
        self.stdout.write(f'✓ DEBUG = {settings.DEBUG}')
        self.stdout.write(f'✓ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}')
        self.stdout.write(f'✓ DATABASE = {settings.DATABASES["default"]["ENGINE"]}')
        self.stdout.write(f'✓ Python version = {sys.version}')
        
        # Test database connection
        from django.db import connection
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database error: {e}'))
            
        self.stdout.write(self.style.SUCCESS('\n=== APP READY ===' ))
