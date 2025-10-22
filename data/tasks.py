"""
Celery Tasks для ProMonitor.kz
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name='poll_modbus_connections')
def poll_modbus_connections():
    """
    Опрашивает все активные Modbus подключения
    """
    from data.models import ModbusConnection
    from data.services.modbus_service import ModbusService
    
    logger.info("Starting Modbus polling task")
    
    connections = ModbusConnection.objects.filter(enabled=True)
    results = {'total': connections.count(), 'success': 0, 'errors': 0}
    
    for connection in connections:
        try:
            service = ModbusService(connection)
            result = service.poll_all_registers()
            results['success'] += 1
            logger.info(f"✓ {connection.name}: Read {result['registers_read']} registers")
        except Exception as e:
            results['errors'] += 1
            logger.error(f"✗ {connection.name}: {e}")
    
    return results


@shared_task(name='cleanup_old_modbus_logs')
def cleanup_old_modbus_logs(days=7):
    """
    Удаляет старые логи Modbus
    """
    from datetime import timedelta
    from data.models import ModbusConnectionLog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = ModbusConnectionLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old Modbus logs")
    return {'deleted_count': deleted_count}

