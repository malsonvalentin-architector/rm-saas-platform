"""
Django management command to set all users to dark theme
"""
from django.core.management.base import BaseCommand
from data.models import User_profile

class Command(BaseCommand):
    help = 'Set all users to dark theme for Dashboard V2'

    def handle(self, *args, **options):
        updated_count = User_profile.objects.filter(theme='light').update(theme='dark')
        null_count = User_profile.objects.filter(theme__isnull=True).update(theme='dark')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} users from light to dark theme'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set theme for {null_count} users with null theme'
            )
        )
        
        # Display all users and their themes
        self.stdout.write('\nCurrent user themes:')
        for user in User_profile.objects.all():
            self.stdout.write(f'  - {user.email}: theme={user.theme}')
