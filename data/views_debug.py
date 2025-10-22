"""
DEBUG VIEWS для диагностики Railway
Временный файл для проверки наличия данных
"""

from django.http import JsonResponse
from django.db import connection
from data.models import Actuator, System, Company, Obj


def debug_actuators_count(request):
    """
    Публичный endpoint для проверки наличия актуаторов
    БЕЗ авторизации - только для диагностики
    """
    try:
        # Информация о базе данных
        db_info = {
            'database': connection.settings_dict['NAME'],
            'engine': connection.settings_dict['ENGINE'],
        }
        
        # Подсчёт объектов в базе
        counts = {
            'companies': Company.objects.count(),
            'objects': Obj.objects.count(),
            'systems': System.objects.count(),
            'actuators': Actuator.objects.count(),
        }
        
        # Детали актуаторов
        actuators_details = []
        for act in Actuator.objects.all()[:10]:
            actuators_details.append({
                'id': act.id,
                'name': act.name,
                'type': act.actuator_type,
                'system': act.sys.name if act.sys else None,
                'is_active': act.is_active,
                'created_at': act.created_at.isoformat() if act.created_at else None,
            })
        
        return JsonResponse({
            'status': 'success',
            'database': db_info,
            'counts': counts,
            'actuators_sample': actuators_details,
            'message': f"Found {counts['actuators']} actuators in database"
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)
