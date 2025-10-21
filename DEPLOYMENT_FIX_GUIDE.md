# 🔧 Руководство по исправлению deployment-проблем ProMonitor.kz

## 🚨 Текущая проблема (Day 4, iteration 8)

**Симптом:** Admin страница `/admin/data/subscriptionplan/` падает с ошибкой:
```
ProgrammingError: column data_subscriptionplan.created_at does not exist
```

**Причина:** Миграция 0007 была применена частично - таблица `SubscriptionPlan` существует, но не имеет полей `created_at` и `updated_at`.

---

## ✅ Решение 1: Автоматическое (рекомендуется)

Railway автоматически выполнит исправление при следующем деплое через команду в `start_web.sh`:

```bash
python manage.py fix_subscription_schema
```

**Проверка успешности:**
1. Откройте https://www.promonitor.kz/admin/data/subscriptionplan/
2. Если страница загружается без ошибок - **исправление сработало!**
3. Проверьте логи Railway на наличие строк:
   ```
   STEP 1.5/5: Fixing SubscriptionPlan Schema
   ✅ created_at добавлена
   ✅ updated_at добавлена
   ```

---

## 🔧 Решение 2: Ручное (если автоматика не сработала)

### Вариант A: Через Railway CLI

```bash
# 1. Установите Railway CLI (если ещё не установлен)
npm install -g @railway/cli

# 2. Авторизуйтесь
railway login

# 3. Подключитесь к проекту
railway link

# 4. Выполните команду напрямую
railway run python manage.py fix_subscription_schema
```

### Вариант B: Через PostgreSQL напрямую

```bash
# 1. Подключитесь к БД Railway через CLI
railway connect postgres

# 2. В psql консоли выполните:
ALTER TABLE data_subscriptionplan 
ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE data_subscriptionplan 
ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

# 3. Проверьте структуру таблицы
\d data_subscriptionplan;

# 4. Выйдите
\q
```

### Вариант C: Через Railway Web Interface

1. Откройте Railway Dashboard → Ваш проект → PostgreSQL service
2. Перейдите в вкладку **Connect**
3. Скопируйте **Database URL**
4. Используйте любой PostgreSQL клиент (pgAdmin, DBeaver, TablePlus)
5. Выполните SQL из Варианта B

---

## 📋 Проверка исправления

После применения любого из решений:

```bash
# Проверьте структуру таблицы
railway run python manage.py dbshell
\d data_subscriptionplan;

# Должны увидеть поля:
# created_at | timestamp with time zone
# updated_at | timestamp with time zone
```

**Веб-проверка:**
1. Откройте https://www.promonitor.kz/admin/
2. Войдите: `admin@promonitor.kz` / `ProMonitor2025!`
3. Перейдите в **Data** → **Subscription plans**
4. Страница должна загрузиться без ошибок

---

## 🔄 Следующие шаги после исправления

После успешного исправления схемы БД:

### 1. Загрузить тарифные планы

```bash
railway run python manage.py load_subscription_plans
```

**Результат:** Создаст 12 тарифов:
- 3 базовых тарифа (BASIC, PROFESSIONAL, ENTERPRISE)
- 9 дополнительных модулей (3 типа × 3 уровня)

### 2. Проверить в админке

- **Subscription plans**: https://www.promonitor.kz/admin/data/subscriptionplan/
- **Addon modules**: https://www.promonitor.kz/admin/data/addonmodule/

### 3. Загрузить демо-данные (опционально)

```bash
railway run python manage.py load_demo_data --user admin@promonitor.kz
```

**Результат:**
- 3 объекта (дата-центр, офис, производство)
- 15+ систем контроллеров
- 40+ датчиков (температура, влажность, давление, мощность)
- 11,520 показаний (последние 24 часа)
- 10+ правил тревог

---

## 🐛 Исправленные баги в этом коммите

### Commit: `72fd2ad` - "feat: add auto-fix for SubscriptionPlan schema on startup"

**1. Миграция 0007** (`data/migrations/0007_subscription_system_v2.py`)
```python
# ДОБАВЛЕНО:
migrations.AddField(
    model_name='subscriptionplan',
    name='created_at',
    field=models.DateTimeField(auto_now_add=True, null=True),
),
migrations.AddField(
    model_name='subscriptionplan',
    name='updated_at',
    field=models.DateTimeField(auto_now=True, null=True),
),
```

**2. load_demo_data.py** (`data/management/commands/load_demo_data.py`)
```python
# ИСПРАВЛЕНО:
# ❌ БЫЛО: sys=system, is_active=...
# ✅ СТАЛО: company=user.company, enabled=...

# ❌ БЫЛО: condition='greater_than'
# ✅ СТАЛО: condition='>'

# ❌ БЫЛО: from django.utils import timezone; timezone.models.Max
# ✅ СТАЛО: from django.db.models import Max; Max('value')
```

**3. Новая management команда** (`data/management/commands/fix_subscription_schema.py`)
- Проверяет наличие полей `created_at` и `updated_at`
- Добавляет их, если отсутствуют
- Показывает текущую структуру таблицы

**4. Автоматика в start_web.sh**
```bash
# STEP 1.5/5: Fixing SubscriptionPlan Schema
python manage.py fix_subscription_schema
```

---

## 📊 Текущий статус деплоя

**✅ Работает:**
- Admin login (https://www.promonitor.kz/admin/)
- Dashboard (https://www.promonitor.kz/dashboard/)
- CSRF защита
- Базовая навигация
- PostgreSQL подключение
- Celery worker (фоновые задачи)

**🔧 Исправлено в этом коммите:**
- SubscriptionPlan schema (created_at/updated_at)
- AlertRule создание в load_demo_data
- Импорт Max из django.db.models

**⏳ Осталось сделать (Фаза 3):**
- User role system (Admin/Manager/Client)
- Admin overview dashboard
- Client portal `/client/dashboard/`
- Multi-tenant subscription management

---

## 🆘 Если ничего не помогло

1. **Проверьте логи Railway:**
   ```bash
   railway logs
   ```

2. **Проверьте состояние БД:**
   ```bash
   railway run python manage.py showmigrations
   ```

3. **Откатите миграцию и повторите:**
   ```bash
   railway run python manage.py migrate data 0006
   railway run python manage.py migrate data 0007
   ```

4. **Пересоздайте таблицу (КРАЙНИЙ СЛУЧАЙ!):**
   ```sql
   -- ⚠️ УДАЛИТ ВСЕ ДАННЫЕ В SUBSCRIPTIONPLAN!
   DROP TABLE data_subscriptionplan CASCADE;
   -- Затем повторно примените миграцию
   railway run python manage.py migrate data 0007
   ```

---

## 📞 Контакты

- **GitHub Repo**: https://github.com/malsonvalentin-architector/rm-saas-platform
- **Production**: https://www.promonitor.kz/
- **Admin Panel**: https://www.promonitor.kz/admin/
- **Railway Project**: [Your Railway Dashboard]

---

**Последнее обновление:** 2025-10-21 (Day 4, Iteration 8)  
**Автор:** AI Assistant (Genspark)  
**Статус:** ✅ Исправления задеплоены, ожидаем подтверждение от пользователя
