"""
Management command для полной очистки и перезагрузки demo данных
Удаляет все объекты, системы, датчики, данные и alert rules
Затем загружает свежие качественные demo данные
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

from data.models import Company, Obj, System, Atributes, Data, AlertRule

User = get_user_model()


class Command(BaseCommand):
    help = 'Reset all demo data and reload quality demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin@promonitor.kz',
            help='User email for demo data'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompt'
        )

    def handle(self, *args, **options):
        user_email = options['user']
        confirm = options['confirm']

        self.stdout.write('=' * 80)
        self.stdout.write(self.style.WARNING('🗑️  ProMonitor Demo Data RESET'))
        self.stdout.write('=' * 80)
        self.stdout.write('')

        # Get user and company
        try:
            user = User.objects.get(email=user_email)
            company = user.company
            self.stdout.write(f'Target user: {user.email}')
            self.stdout.write(f'Target company: {company.name}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User not found: {user_email}'))
            return

        # Count current data
        obj_count = Obj.objects.filter(company=company).count()
        sys_count = System.objects.filter(obj__company=company).count()
        attr_count = Atributes.objects.filter(sys__obj__company=company).count()
        data_count = Data.objects.filter(name__sys__obj__company=company).count()
        alert_count = AlertRule.objects.filter(company=company).count()

        self.stdout.write('')
        self.stdout.write('📊 Current data:')
        self.stdout.write(f'   Objects:     {obj_count}')
        self.stdout.write(f'   Systems:     {sys_count}')
        self.stdout.write(f'   Sensors:     {attr_count}')
        self.stdout.write(f'   Data points: {data_count}')
        self.stdout.write(f'   Alert rules: {alert_count}')
        self.stdout.write('')

        if not confirm:
            self.stdout.write(self.style.WARNING('⚠️  This will DELETE ALL data for this company!'))
            response = input('Type "yes" to confirm: ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Cancelled'))
                return

        # Delete all data
        self.stdout.write('')
        self.stdout.write('🗑️  Deleting old data...')
        
        # Delete in correct order (FK constraints)
        deleted_data = Data.objects.filter(name__sys__obj__company=company).delete()
        self.stdout.write(f'   ✅ Data points deleted: {deleted_data[0]}')
        
        deleted_alerts = AlertRule.objects.filter(company=company).delete()
        self.stdout.write(f'   ✅ Alert rules deleted: {deleted_alerts[0]}')
        
        deleted_attrs = Atributes.objects.filter(sys__obj__company=company).delete()
        self.stdout.write(f'   ✅ Sensors deleted: {deleted_attrs[0]}')
        
        deleted_systems = System.objects.filter(obj__company=company).delete()
        self.stdout.write(f'   ✅ Systems deleted: {deleted_systems[0]}')
        
        deleted_objects = Obj.objects.filter(company=company).delete()
        self.stdout.write(f'   ✅ Objects deleted: {deleted_objects[0]}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ All old data deleted!'))
        self.stdout.write('')

        # Load new quality demo data
        self.stdout.write('📥 Loading quality demo data...')
        self.stdout.write('')
        
        call_command('load_quality_demo', user=user_email)

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ Demo data reset completed!'))
        self.stdout.write('=' * 80)
        self.stdout.write('')
        self.stdout.write('🌐 Access at: https://www.promonitor.kz/objects/')
        self.stdout.write('')
