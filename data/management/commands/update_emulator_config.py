from django.core.management.base import BaseCommand
from data.models import ModbusConnection

class Command(BaseCommand):
    help = 'Update Modbus Emulator connection to Railway service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--emulator-url',
            type=str,
            required=True,
            help='URL эмулятора на Railway'
        )

    def handle(self, *args, **options):
        emulator_url = options['emulator_url']
        
        try:
            connection = ModbusConnection.objects.get(name="Enhanced Emulator v2.0")
            
            # Очищаем URL
            clean_host = emulator_url.replace('https://', '').replace('http://', '').rstrip('/')
            
            old_host = connection.host
            old_port = connection.port
            
            connection.host = clean_host
            connection.port = 8000  # Railway использует порт 8000
            connection.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Emulator connection updated!'))
            self.stdout.write(f'   Old: {old_host}:{old_port}')
            self.stdout.write(f'   New: {clean_host}:8000')
            
        except ModbusConnection.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Enhanced Emulator v2.0 not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
