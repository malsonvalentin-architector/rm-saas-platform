#!/usr/bin/env python3
"""
Скрипт для обновления URL и логотипа в templates
"""
import re
import os

TEMPLATES_DIR = "templates/dashboard/v2"

# Старый и новый URL логотипа
OLD_LOGO_URL = "https://page.gensparksite.com/v1/base64_upload/d06065d78d89c7b1e9da41e59e5198a1"
NEW_LOGO_URL = "https://page.gensparksite.com/v1/base64_upload/b3a3a416e4d3b1d74a52edd01729c28e"

# Файлы для обработки
FILES = [
    "sensors.html",
    "alerts.html",
    "analytics.html",
    "reports.html",
    "settings.html",
    "users.html",
]

def update_file(filepath, active_page=None):
    """Обновляет URL и логотип в файле"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Обновляем URL логотипа
    content = content.replace(OLD_LOGO_URL, NEW_LOGO_URL)
    
    # 2. Обновляем URL навигации
    content = content.replace('href="/dashboard/main/"', 'href="/dashboard/"')
    content = content.replace('href="/dashboard/v2/', 'href="/dashboard/')
    
    # 3. Обновляем active class для текущей страницы
    if active_page:
        # Убираем все active классы
        content = re.sub(r'class="nav-link active"', 'class="nav-link"', content)
        
        # Добавляем active для нужной страницы
        pattern = f'href="/dashboard/{active_page}/" class="nav-link"'
        replacement = f'href="/dashboard/{active_page}/" class="nav-link active"'
        content = content.replace(pattern, replacement)
    
    # 4. Обновляем стили логотипа (убираем mix-blend-mode, добавляем новый дизайн)
    # Находим .sidebar-header
    old_sidebar_header = r'\.sidebar-header\s*\{[^}]+\}'
    new_sidebar_header = """.sidebar-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 2px solid var(--border-color);
            background: linear-gradient(180deg, var(--bg-secondary) 0%, #141922 100%);
            min-height: 85px;
            display: flex;
            align-items: center;
            justify-content: center;
        }"""
    content = re.sub(old_sidebar_header, new_sidebar_header, content)
    
    # Находим .logo-container
    old_logo_container = r'\.logo-container\s*\{[^}]+\}'
    new_logo_container = """.logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 220px;
            margin: 0 auto;
            padding: 0.5rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }"""
    content = re.sub(old_logo_container, new_logo_container, content)
    
    # Находим .logo
    old_logo = r'\.logo\s*\{[^}]+\}'
    new_logo = """.logo {
            width: 100%;
            height: auto;
            filter: brightness(1.1) contrast(1.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            object-fit: contain;
        }"""
    content = re.sub(old_logo, new_logo, content)
    
    # Находим .logo:hover
    old_logo_hover = r'\.logo:hover\s*\{[^}]+\}'
    new_logo_hover = """.logo:hover {
            filter: brightness(1.2) contrast(1.15) drop-shadow(0 4px 16px rgba(66, 153, 225, 0.4));
            transform: scale(1.03);
        }
        
        .logo-container:hover {
            background: rgba(0, 0, 0, 0.4);
            box-shadow: 0 6px 20px rgba(66, 153, 225, 0.3);
        }"""
    content = re.sub(old_logo_hover, new_logo_hover, content)
    
    # Записываем обновленный контент
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {os.path.basename(filepath)}")

def main():
    print("=== Обновление URL и логотипа ===\n")
    
    # Мапинг файл -> активная страница
    active_pages = {
        "sensors.html": "sensors",
        "alerts.html": "alerts",
        "analytics.html": "analytics",
        "reports.html": "reports",
        "settings.html": "settings",
        "users.html": "users",
    }
    
    for filename in FILES:
        filepath = os.path.join(TEMPLATES_DIR, filename)
        active_page = active_pages.get(filename)
        update_file(filepath, active_page)
    
    print("\n✅ Все файлы обновлены!")
    print("\nНовая структура URL:")
    print("  /dashboard/ - главная")
    print("  /dashboard/buildings/ - здания")
    print("  /dashboard/sensors/ - сенсоры")
    print("  /dashboard/alerts/ - оповещения")
    print("  /dashboard/reports/ - отчеты")
    print("  /dashboard/analytics/ - аналитика")
    print("  /dashboard/settings/ - настройки")
    print("  /dashboard/users/ - пользователи")
    print("\nЛоготип обновлен на версию для темной темы!")

if __name__ == "__main__":
    main()
