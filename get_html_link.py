# Просто выведем содержимое файла для просмотра
with open('/home/user/rm/django_admin_report.html', 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"Размер файла: {len(content)} байт")
    print("Первые 500 символов:")
    print(content[:500])
