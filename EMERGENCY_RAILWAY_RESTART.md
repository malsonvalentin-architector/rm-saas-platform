# 🚨 EMERGENCY: Railway Application Failed to Respond

## Проблема
Railway показывает ошибку: **"Application failed to respond"**

Это означает что приложение либо:
1. Упало во время startup
2. Не смогло подключиться к базе данных
3. Один из management commands завис
4. Не слушает на правильном PORT

---

## ✅ БЫСТРОЕ РЕШЕНИЕ

### Вариант 1: Перезапуск через Railway Dashboard (РЕКОМЕНДУЕТСЯ)

1. **Откройте Railway Dashboard:**
   ```
   https://railway.app/dashboard
   ```

2. **Найдите проект `rm-saas-platform`**

3. **Перейдите во вкладку "Deployments"**

4. **Нажмите на последний deployment (самый верхний)**

5. **Справа вверху найдите кнопку "..." (три точки)**

6. **Выберите "Redeploy"** или **"Restart"**

7. **Дождитесь завершения (2-3 минуты)**

8. **Проверьте Deploy Logs:**
   - Найдите строку: `🚀 Daphne starting on 0.0.0.0:XXXX`
   - Убедитесь что нет ошибок (красные строки)

9. **После успешного деплоя откройте:**
   ```
   https://www.promonitor.kz/
   ```

---

### Вариант 2: Проверка Deploy Logs

Если перезапуск не помог, проверьте логи:

1. **Railway Dashboard → Deployments → Последний deployment**

2. **Вкладка "Deploy Logs"**

3. **Найдите ошибки:**
   - `❌ FATAL:` - критическая ошибка
   - `ModuleNotFoundError` - не хватает зависимости
   - `OperationalError` - проблема с базой данных
   - `CommandError` - ошибка в management command

4. **Частые ошибки:**

   **A) Database connection failed:**
   ```
   OperationalError: could not connect to server
   ```
   **Решение:**
   - Railway Dashboard → PostgreSQL plugin
   - Проверьте что DATABASE_URL переменная установлена
   - Перезапустите PostgreSQL plugin

   **B) Migration failed:**
   ```
   django.db.migrations.exceptions.InconsistentMigrationHistory
   ```
   **Решение:**
   - Нужно сбросить миграции (опасно, удалит данные!)
   - Или откатить на предыдущий working commit

   **C) Management command hung:**
   ```
   STEP X/Y: [название команды]
   (и дальше ничего не происходит)
   ```
   **Решение:**
   - Команда зависла, нужно её отключить
   - Закомментировать в `start_web.sh`

---

### Вариант 3: Откат на предыдущий working commit

Если новые изменения сломали деплой:

1. **Найдите последний рабочий commit:**
   ```
   918a1e1 Phase 4.2: Objects Management UI - COMPLETE!
   ```

2. **Railway Dashboard → Settings → "GitHub Repo"**

3. **Нажмите "Disconnect" и затем "Reconnect"**

4. **Выберите branch и commit:**
   - Branch: `main`
   - Commit: `918a1e1` (последний рабочий)

5. **Railway автоматически задеплоит старую версию**

6. **Проверьте что сайт работает**

7. **Потом можно постепенно применять новые коммиты**

---

### Вариант 4: Manual Railway CLI

Если у вас установлен Railway CLI:

```bash
# Login
railway login

# Link project
railway link

# View logs in real-time
railway logs

# Restart service
railway service restart

# Check status
railway status
```

---

## 🔍 ДИАГНОСТИКА

### Проверка 1: Database доступна?
```bash
# Railway Dashboard → PostgreSQL plugin
# Проверьте статус: должен быть зелёный "Active"
```

### Проверка 2: Правильные environment variables?
```bash
# Railway Dashboard → Web Service → Variables
# Должны быть:
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=www.promonitor.kz,promonitor.kz
```

### Проверка 3: Build прошёл успешно?
```bash
# Railway Dashboard → Deployment → Build Logs
# Последняя строка должна быть:
# "Build completed successfully"
```

### Проверка 4: Start command правильный?
```bash
# Railway Dashboard → Settings → Deploy
# Start Command должен быть:
web: bash start_web.sh
```

---

## 🛠️ ВРЕМЕННОЕ РЕШЕНИЕ

Если нужно **СРОЧНО** восстановить работу сайта:

1. **Откатитесь на commit `918a1e1`** (последний 100% рабочий)

2. **После того как сайт заработает:**
   - Проверьте что конкретно сломалось
   - Исправьте проблему
   - Задеплойте снова

---

## 📋 ЧЕКЛИСТ ДЛЯ ПРОВЕРКИ

После перезапуска проверьте:

- [ ] Railway Deployment статус = "Success" (зелёный)
- [ ] Deploy Logs показывают: `🚀 Daphne starting...`
- [ ] Нет ошибок в Deploy Logs (красных строк)
- [ ] `https://www.promonitor.kz/` открывается
- [ ] Страница логина загружается
- [ ] Можно залогиниться (admin@promonitor.kz / Vika2025)
- [ ] Dashboard открывается после логина
- [ ] `/objects/` показывает список объектов

---

## 🆘 ЕСЛИ НИЧЕГО НЕ ПОМОГЛО

**Пришлите мне скриншоты:**

1. Railway Dashboard → Deployments (весь список)
2. Последний Deployment → Deploy Logs (весь вывод)
3. Railway Dashboard → PostgreSQL → Status
4. Railway Dashboard → Web Service → Variables (замажьте секреты)
5. Browser console (F12) при попытке открыть сайт

**Или скопируйте текст:**
- Последние 100 строк из Deploy Logs
- Error messages (если есть красные строки)

---

## 📞 КОНТАКТЫ

**Railway Support:**
- https://railway.app/help
- Discord: https://discord.gg/railway

**Документация:**
- Railway Docs: https://docs.railway.app/
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

**Создано:** 2025-10-21 11:15 UTC  
**Последний working commit:** `918a1e1`  
**Проблемный commit:** `1858055` (URL fix)  
**Status:** 🔴 APPLICATION DOWN - требуется restart
