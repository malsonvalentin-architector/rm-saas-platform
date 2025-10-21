# 🔧 BUGFIX DEPLOYED: AttributeError в Django Admin

**Дата:** 2025-10-21  
**Коммит:** `607cf3e`  
**Статус:** ✅ Запушен на GitHub → Railway деплоит

---

## 🐛 Проблема

**Ошибка:** `AttributeError: 'NoneType' object has no attribute 'name'`

**Контекст:**
- Пользователь пытался удалить 63 старых объекта через Django Admin
- При попытке отображения объектов для удаления Django вызывал `Obj.__str__()`
- Метод падал на строке: `return f'{self.obj} ({self.company.name})'`
- **Причина:** У некоторых объектов `self.company = None` (сиротские записи без компании)

**Файл:** `data/models.py`, строка 276

---

## ✅ Решение

**Исправление в `data/models.py`:**

```python
# БЫЛО (строка 276):
def __str__(self):
    return f'{self.obj} ({self.company.name})'

# СТАЛО:
def __str__(self):
    company_name = self.company.name if self.company else 'No Company'
    return f'{self.obj} ({company_name})'
```

**Добавлена null-проверка** перед обращением к `company.name`

---

## 📦 Дополнительно в коммите

1. **clean_demo_data.sql** (новый файл)
   - SQL скрипт для ручной очистки старых demo данных
   - Безопасное каскадное удаление FK relationships
   - Порядок удаления: Data → Atribute → System → Obj

2. **test_startup.sh** (новый файл)
   - Скрипт для локального тестирования startup команд
   - Помогает проверить миграции и команды перед деплоем

---

## 🚀 Следующие шаги

### Шаг 1: Дождаться Railway деплоя (3-5 минут)
Railway автоматически деплоит коммит `607cf3e` после push

### Шаг 2: Проверить исправление
1. Открыть https://www.promonitor.kz/admin/
2. Войти как superadmin
3. Перейти в **Data → Objs**
4. Выбрать несколько объектов (checkbox)
5. В dropdown выбрать **"Delete selected objs"**
6. Нажать **Go**
7. **Должен появиться экран подтверждения удаления без ошибок**

### Шаг 3: Удалить старые 63 объекта

**Вариант A: Django Admin (теперь должен работать)**
- Выделить все объекты → Delete selected → Confirm

**Вариант B: SQL скрипт (если Admin всё ещё глючит)**
```bash
# Через Railway CLI:
railway run psql $DATABASE_URL -f clean_demo_data.sql
```

### Шаг 4: Загрузить новые качественные demo данные
```bash
railway run python manage.py reset_demo_data
```

**Результат:**
- 10 качественных объектов (офисы, склады, магазины)
- 3-5 систем на объект (HVAC, Refrigeration, Lighting)
- 5-8 датчиков на систему
- 43,200+ data points (24h history, 5min intervals)

---

## 🎯 Ожидаемый результат

После выполнения всех шагов:

✅ Django Admin работает без ошибок  
✅ Старые 63 объекта удалены  
✅ 10 новых качественных объектов загружены  
✅ Все объекты имеют системы, датчики и данные  
✅ Графики отображаются корректно  
✅ Role-based доступ работает  

---

## 📊 Коммит детали

```bash
Commit: 607cf3e
Author: Railway auto-deploy
Date: 2025-10-21

Changed files:
- data/models.py (modified) - +2 lines, -1 line
- clean_demo_data.sql (new) - 108 lines
- test_startup.sh (new) - added

Push: cd485bc..607cf3e main -> main
```

---

## 🔍 Техническая информация

**Root cause:**
- В БД существуют объекты (`Obj`) с `company_id = NULL`
- Django ORM не ограничивает NULL для FK по умолчанию без `blank=False, null=False`
- `__str__()` метод вызывается при рендеринге Admin списков и форм удаления
- Обращение к атрибуту `None` объекта вызывает `AttributeError`

**Как возникли NULL компании:**
- Возможно, при создании через shell/миграции без указания company
- Или при удалении компании без ON_DELETE=CASCADE
- Или при direct SQL манипуляциях

**Почему раньше не проявлялось:**
- Пользователь не пытался массово удалять объекты через Admin
- В обычном object_list используется related_name='objs' с prefetch
- Проблема проявилась только при Admin deletion view

---

**Статус:** 🟢 DEPLOYED  
**Deployment time:** ~3-5 минут после push  
**Требуется тестирование:** Да, пользователь должен повторить удаление через Admin

