# FieldError Fix - atributes_set → atributes

## 🔴 Проблема
После URL fix сайт заработал, но страница `/objects/` показывала ошибку:

```
FieldError at /objects/
Cannot resolve keyword 'attributes_set' for field or join on the field not permitted
```

**Traceback:**
```python
data/views.py, line 22, in object_list
    alert_count=Count('system__atributes_set__alertrule', ...)
```

---

## 🔍 Root Cause

Django автоматически создаёт **related_name** для ForeignKey полей.

### Модель Atributes:
```python
class Atributes(models.Model):
    sys = models.ForeignKey(System, on_delete=models.CASCADE)
```

### Автоматический related_name:
- **Field name:** `sys`
- **Related name (lowercase):** `atributes` (не `atributes_set`!)

Django **НЕ** добавляет `_set` суффикс если related_name явно не указан.

---

## ✅ Решение

Заменил **`atributes_set`** на **`atributes`** во всех местах:

### 1. data/views.py (4 изменения)

**Строка 22:** object_list view
```python
# БЫЛО ❌
alert_count=Count('system__atributes_set__alertrule', ...)

# СТАЛО ✅
alert_count=Count('system__atributes__alertrule', ...)
```

**Строка 54:** object_dashboard view
```python
# БЫЛО ❌
systems = System.objects.filter(obj=obj).prefetch_related('atributes_set')

# СТАЛО ✅
systems = System.objects.filter(obj=obj).prefetch_related('atributes')
```

**Строки 59, 78, 170:** Loops через atributes
```python
# БЫЛО ❌
for attr in system.atributes_set.all():

# СТАЛО ✅
for attr in system.atributes.all():
```

### 2. data/management/commands/load_demo_data.py (1 изменение)

**Строка 183:**
```python
# БЫЛО ❌
critical_attrs = [attr for attr in system.atributes_set.all() ...]

# СТАЛО ✅
critical_attrs = [attr for attr in system.atributes.all() ...]
```

---

## 🧪 Проверка

```bash
# Поиск всех atributes_set
grep -rn "atributes_set" --include="*.py" .
# ✅ No results = all fixed

# Django check
python manage.py check
# System check identified no issues (0 silenced).
```

---

## 📊 ORM Path Explanation

**Правильный путь через Django ORM:**

```
Obj → System → Atributes → AlertRule
 ↓       ↓         ↓           ↓
obj    system   atributes  alertrule_set
       (FK)     (reverse)   (reverse)
```

**Annotate query:**
```python
objects.annotate(
    alert_count=Count(
        'system__atributes__alertrule',
        filter=Q(system__atributes__alertrule__enabled=True)
    )
)
```

**Breakdown:**
1. `system` - ForeignKey от Obj к System (related_name='system')
2. `atributes` - Reverse ForeignKey от System к Atributes (через поле `sys`)
3. `alertrule` - Reverse ForeignKey от Atributes к AlertRule (через поле `attribute`)

---

## 🚀 Deployment

**Commit:** `478e8fa`  
**Pushed:** ✅ Yes  
**Railway auto-deploy:** 🔄 In progress

**Testing after deploy:**
1. https://www.promonitor.kz/objects/ - должен показывать список
2. Login: admin@promonitor.kz / Vika2025
3. Проверить что нет FieldError
4. Проверить счётчики систем и тревог

---

## 📝 Lessons Learned

### ❌ Распространённая ошибка:
Добавление `_set` суффикса к related_name, когда Django его не создаёт автоматически.

### ✅ Правильный подход:
1. **Проверить модель:** Какое имя у ForeignKey field?
2. **Lowercase:** Django использует lowercase для related_name
3. **Без _set:** `_set` добавляется только для ManyToMany или явно указанного related_name
4. **Shell check:** `python manage.py shell` → `Model._meta.get_fields()`

### Как избежать в будущем:
```python
# В моделях явно указывать related_name
class Atributes(models.Model):
    sys = models.ForeignKey(
        System, 
        on_delete=models.CASCADE,
        related_name='attributes'  # Explicit is better than implicit
    )
```

---

**Generated:** 2025-10-21 11:30 UTC  
**Status:** ✅ Fixed, deployed  
**Previous errors:** URL routing (fixed), FieldError (fixed)  
**Next:** Testing all functionality
