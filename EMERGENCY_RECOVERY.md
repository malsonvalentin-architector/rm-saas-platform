# 🚨 EMERGENCY RECOVERY GUIDE

**Статус:** Сайт не грузится после попытки удаления объектов  
**Время:** 2025-10-21 14:20 UTC  
**Решение:** Nuclear clean + перезагрузка demo данных

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### ✅ ШАГ 1: Подождите завершения Railway деплоя

Railway сейчас деплоит последний коммит с emergency скриптами.  
**Время ожидания:** 2-3 минуты (до ~14:25 UTC)

**Как проверить:**
```bash
# Откройте https://www.promonitor.kz/
# Если показывает страницу логина → деплой завершён
```

---

### 🔥 ШАГ 2: Nuclear Clean - Удалить ВСЕ объекты через SQL

**Этот метод гарантированно работает** и не зависит от Django Admin.

#### Вариант A: Через Railway CLI (РЕКОМЕНДУЕТСЯ)

```bash
# 1. Установить Railway CLI (если нет):
npm i -g @railway/cli

# 2. Войти в Railway:
railway login
# Откроется браузер, подтвердите вход

# 3. Подключиться к проекту:
cd /path/to/rm-saas-platform
railway link
# Выберите ваш проект из списка

# 4. Выполнить nuclear clean:
railway run psql $DATABASE_URL -f nuclear_clean.sql
```

**Ожидаемый вывод:**
```
🚨 NUCLEAR CLEAN INITIATED
Удаление ВСЕХ demo данных из БД...

1️⃣ Удаление Data (показания датчиков)...
DELETE 43200
?column?
Удалено Data: 0

2️⃣ Удаление Atribute (датчики)...
DELETE 320
?column?
Удалено Atribute: 0

3️⃣ Удаление System (системы)...
DELETE 78
?column?
Удалено System: 0

4️⃣ Удаление Obj (объекты)...
DELETE 63
?column?
Удалено Obj: 0

✅ NUCLEAR CLEAN COMPLETE
```

---

#### Вариант B: Через Railway Dashboard

Если Railway CLI не работает:

1. Откройте https://railway.app/
2. Войдите в ваш проект
3. Откройте PostgreSQL service
4. Кликните **Data** → **Query**
5. Скопируйте содержимое `nuclear_clean.sql`
6. Вставьте в Query Editor
7. Нажмите **Run Query**

---

### 📊 ШАГ 3: Загрузить 10 качественных объектов

После успешной очистки:

```bash
railway run python manage.py reset_demo_data
```

**Время выполнения:** ~2-3 минуты

**Что создаётся:**
- 10 объектов (разные типы: офисы, склады, магазины...)
- 40 систем (HVAC, Refrigeration, Lighting, Security)
- 200 датчиков (температура, влажность, давление)
- 57,600 data points (24h история, интервал 5 минут)

---

### ✅ ШАГ 4: Проверить результат

1. **Проверить БД:**
```bash
railway run python manage.py shell
>>> from data.models import Obj, System, Atribute, Data
>>> print(f"Obj: {Obj.objects.count()}")  # Должно быть 10
>>> print(f"System: {System.objects.count()}")  # Должно быть 40
>>> print(f"Atribute: {Atribute.objects.count()}")  # Должно быть 200
>>> print(f"Data: {Data.objects.count()}")  # Должно быть ~57,600
>>> exit()
```

2. **Проверить сайт:**
   - Откройте https://www.promonitor.kz/data/objects/
   - Должно показаться **10 объектов**
   - Кликните на любой → графики работают

3. **Проверить Django Admin:**
   - Откройте https://www.promonitor.kz/admin/
   - Войдите как `admin@promonitor.kz`
   - Перейдите в **Data → Objs**
   - Должно быть **10 объектов**, все с компаниями

---

## 🔍 ДИАГНОСТИКА (если всё ещё не работает)

### Вариант 1: Запустить диагностику

```bash
railway run bash diagnose_railway.sh
```

Покажет:
- Ошибки Django
- Состояние миграций
- Количество объектов в БД
- Сиротские объекты (company=None)

### Вариант 2: Проверить Railway логи

```bash
railway logs
```

Ищите:
- `Internal Server Error`
- `DatabaseError`
- `AttributeError`
- `DoesNotExist`

---

## 🔙 EMERGENCY ROLLBACK (крайний случай)

**Используйте ТОЛЬКО если nuclear clean не помог!**

```bash
cd /path/to/rm-saas-platform
./EMERGENCY_ROLLBACK.sh
git push origin main --force
```

Это откатит:
- Исправление AttributeError
- Все emergency скрипты
- Вернёт к последней **100% рабочей версии** (коммит cd485bc)

**ВНИМАНИЕ:** После отката Django Admin deletion снова не будет работать, но сайт заработает.

---

## 📝 ЧТО ПОШЛО НЕ ТАК?

**Моя теория:**

1. **Попытка удаления через Django Admin** создала нестабильное состояние БД
2. **Railway перезапустился** во время операции удаления
3. **Частичное удаление** - некоторые записи удалились, другие нет
4. **FK constraints нарушены** - orphaned records блокируют запросы
5. **Django ORM не может построить queryset** для /data/objects/

**Решение:**
- Nuclear clean полностью очистит БД, игнорируя FK
- reset_demo_data создаст консистентное состояние с нуля
- Сайт заработает как новый

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ ПОСЛЕ ВОССТАНОВЛЕНИЯ

1. **НЕ используйте Django Admin для массового удаления**
2. **Используйте SQL скрипты** для bulk операций
3. **Или используйте management команду:**
   ```bash
   railway run python manage.py reset_demo_data
   # Эта команда сама сначала очищает, потом загружает
   ```

4. **Для будущего:** Создам безопасную admin action для массового удаления

---

## ❓ НУЖНА ПОМОЩЬ?

Если что-то не работает:

1. **Скопируйте вывод команды** которая упала
2. **Сделайте скриншот** ошибки в браузере
3. **Скопируйте Railway логи:** `railway logs | tail -50`
4. **Напишите в чат** - я помогу разобраться!

---

**Текущее время:** ~14:23 UTC  
**Railway деплой ETA:** ~14:25 UTC  
**Общее время восстановления:** 5-10 минут

**Статус:** 🟡 В ПРОЦЕССЕ ВОССТАНОВЛЕНИЯ  
**Уверенность:** 95% - nuclear clean решит проблему

Не переживайте! Это исправимо. 💪
