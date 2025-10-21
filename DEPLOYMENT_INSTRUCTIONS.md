# 🚨 CRITICAL: Manual Deployment Fix Required

## Проблема
Railway deployment завершился, но старые demo данные НЕ удалились.

**Причина:** Команда `reset_demo_data` запускается при деплое, но если в БД уже есть данные, она их не трогает (защита от случайного удаления).

---

## ✅ РЕШЕНИЕ (2 ВАРИАНТА)

### Вариант 1: Railway CLI (БЫСТРЕЕ)

Если у вас установлен Railway CLI:

```bash
# 1. Login
railway login

# 2. Link к проекту
railway link

# 3. Запустить reset вручную
railway run python manage.py reset_demo_data --user admin@promonitor.kz --confirm

# 4. Перезапустить web service
railway service restart
```

---

### Вариант 2: Railway Dashboard + PostgreSQL (БЕЗ CLI)

#### Шаг 1: Откройте PostgreSQL в Railway

1. Откройте https://railway.app/dashboard
2. Найдите проект `rm-saas-platform`
3. Кликните на **PostgreSQL** plugin
4. Перейдите в **Data** tab
5. Или используйте **Connect** для psql

#### Шаг 2: Удалите старые данные SQL запросом

```sql
-- Подключитесь к БД и выполните:

-- 1. Найти company_id для admin@promonitor.kz
SELECT id, name FROM data_company WHERE name LIKE '%ProMonitor%';
-- Запомните ID (например, 1)

-- 2. Удалить все данные компании (ЗАМЕНИТЕ 1 на ваш company_id)
DELETE FROM data_data WHERE name_id IN (
    SELECT a.id FROM data_atributes a
    JOIN data_system s ON a.sys_id = s.id
    JOIN data_obj o ON s.obj_id = o.id
    WHERE o.company_id = 1
);

DELETE FROM data_alertrule WHERE company_id = 1;

DELETE FROM data_atributes WHERE sys_id IN (
    SELECT s.id FROM data_system s
    JOIN data_obj o ON s.obj_id = o.id
    WHERE o.company_id = 1
);

DELETE FROM data_system WHERE obj_id IN (
    SELECT id FROM data_obj WHERE company_id = 1
);

DELETE FROM data_obj WHERE company_id = 1;
```

#### Шаг 3: Перезапустите web service

1. Railway Dashboard → Web Service
2. Нажмите **"..."** (три точки) → **Restart**
3. Дождитесь перезапуска (2-3 минуты)
4. При restart автоматически выполнится `reset_demo_data`

---

### Вариант 3: Django Admin (ЧЕРЕЗ БРАУЗЕР)

Если не хотите использовать SQL:

1. Откройте https://www.promonitor.kz/admin/
2. Login: superadmin@promonitor.kz / Super123!
3. Перейдите в **Data → Objects (Obj)**
4. Выберите все объекты (галочка вверху)
5. Actions → **Delete selected objects**
6. Подтвердите удаление

**⚠️ ВНИМАНИЕ:** Это удалит все связанные системы, датчики и данные!

Затем:
1. Railway Dashboard → Web Service → Restart
2. При restart загрузятся новые demo данные

---

## 🔍 ПРОВЕРКА ПОСЛЕ УДАЛЕНИЯ

После выполнения любого варианта проверьте:

1. **Railway Deploy Logs:**
   ```
   ✅ Demo data reset and reloaded!
   📊 Fresh data:
      • 10 realistic objects with full monitoring
   ```

2. **Сайт:**
   ```
   https://www.promonitor.kz/objects/
   ```
   - Должно быть **ровно 10 объектов**
   - Названия: "Дата-центр Алматы", "Офисное здание на Абая" и т.д.

3. **Детальный дашборд:**
   ```
   https://www.promonitor.kz/objects/1/
   ```
   - Gauge показатели **НЕ нули**
   - Системы отображаются
   - Датчики показывают значения

---

## 💡 АЛЬТЕРНАТИВА: Изменить start_web.sh

Если хотите **ПРИНУДИТЕЛЬНО** удалять данные при каждом деплое:

1. Измените в Railway Environment Variables:
   ```
   RESET_DEMO_DATA=true
   ```

2. Обновите start_web.sh:
   ```bash
   if [ "$RESET_DEMO_DATA" = "true" ]; then
       python manage.py reset_demo_data --user admin@promonitor.kz --confirm
   else
       python manage.py load_quality_demo --user admin@promonitor.kz
   fi
   ```

Но это **НЕ рекомендуется** для production!

---

## ❓ Почему это произошло?

**Railway не перезагружает данные автоматически потому что:**

1. `load_quality_demo` проверяет существование объектов
2. Если объекты уже есть → skip загрузки
3. Это защита от дублирования данных

**Правильное решение:**
- Вручную удалить старые данные (1 раз)
- При следующих деплоях будут загружаться свежие данные

---

## 📞 Что делать?

**Выберите один из вариантов выше и выполните.**

После выполнения напишите мне:
- Какой вариант использовали
- Сколько объектов теперь показывается на /objects/
- Работает ли детальный дашборд

Я помогу если возникнут проблемы! 🚀

---

**Created:** 2025-10-21 12:15  
**Status:** ⚠️ MANUAL ACTION REQUIRED  
**Priority:** 🔴 HIGH
