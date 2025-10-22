"""
DEBUG VIEW: Показывает актуальный HTML шаблон
Для диагностики проблем с кешированием
"""

from django.http import HttpResponse
from django.template.loader import get_template


def debug_template_source(request):
    """
    Показывает исходный код шаблона actuators_list.html
    """
    try:
        template = get_template('data/actuators_list.html')
        source = template.template.source
        
        # Ищем строку с modal fade
        lines = source.split('\n')
        modal_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'modal fade' in line.lower() or 'controlModal' in line:
                # Показываем контекст: 2 строки до и после
                start = max(0, i-3)
                end = min(len(lines), i+3)
                context = '\n'.join([f"{j}: {lines[j-1]}" for j in range(start+1, end+1)])
                modal_lines.append(f"\n=== Строка {i} ===\n{context}\n")
        
        html = f"""
        <html>
        <head><title>Debug: Template Source</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h1>Actuators List Template - Modal Lines</h1>
            <p><strong>Template path:</strong> {template.origin.name}</p>
            <p><strong>Total lines:</strong> {len(lines)}</p>
            <hr>
            <h2>All lines containing 'modal fade' or 'controlModal':</h2>
            <pre style="background: #f5f5f5; padding: 15px; overflow-x: auto;">{''.join(modal_lines)}</pre>
            
            <hr>
            <h2>Проверка:</h2>
            <p>✅ Если есть <code>style="display:none;"</code> - фикс применён</p>
            <p>❌ Если НЕТ <code>style="display:none;"</code> - Railway не задеплоил</p>
        </body>
        </html>
        """
        
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"<h1>Error</h1><pre>{str(e)}</pre>")
