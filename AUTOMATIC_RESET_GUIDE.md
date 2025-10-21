# 🤖 АВТОМАТИЧЕСКИЙ СБРОС DEMO ДАННЫХ

**Дата:** 2025-10-21  
**Статус:** ✅ Настроено автоматическое выполнение

---

## 🎯 ЧТО СОЗДАНО

Я создал **3 способа** автоматического сброса demo данных:

### 1️⃣ GitHub Actions (рекомендуется)
**Файл:** `.github/workflows/reset_demo_data.yml`

**Как использовать:**
1. Перейдите на GitHub: https://github.com/malsonvalentin-architector/rm-saas-platform/actions
2. Выберите workflow **"Reset Demo Data on Railway"**
3. Нажмите **"Run workflow"** → **"Run workflow"**
4. Подождите 2-3 минуты
5. ✅ Готово!

**Требования:**
- Нужен Railway Token в GitHub Secrets
- Добавляется в: Settings → Secrets → Actions → New secret
- Name: `RAILWAY_TOKEN`
- Value: получите из Railway Dashboard

### 2️⃣ Python скрипт (прямое выполнение)
**Файл:** `auto_reset_demo.py`

**Как использовать через Railway CLI:**
```bash
railway run --service web python auto_reset_demo.py
```

**Что делает:**
- Удаляет все старые Obj, System, Atribute, Data
- Загружает 10 новых качественных объектов
- Показывает прогресс и результаты

### 3️⃣ Management команда (уже существует)
**Файл:** `data/management/commands/reset_demo_data.py`

**Как использовать:**
```bash
railway run --service web python manage.py reset_demo_data
```

---

## 🚀 БЫСТРЫЙ СТАРТ

### Через PowerShell (Windows):

```powershell
cd C:\Users\Admin\rm-saas-platform
git pull origin main
railway run --service web python auto_reset_demo.py
```

### Через Railway Dashboard:

1. Откройте https://railway.app/project/adventurous-adventure
2. Кликните **web** service
3. Найдите **"..."** (три точки) или **"Actions"**
4. Выберите **"Run Command"** или **"Execute"**
5. Введите: `python auto_reset_demo.py`

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения любого из методов:

```
✅ Deleted Data: 43200 records
✅ Deleted Atribute: 320 records
✅ Deleted System: 78 records
✅ Deleted Obj: 63 records

📊 Loading fresh demo data...
✅ Created: Головной офис ProMonitor
✅ Created: Склад Алматы-1
...
✅ DEMO DATA RESET COMPLETE!

📊 Results:
   Obj: 10
   System: 40
   Atribute: 200
   Data: 57600

🌐 Check: https://www.promonitor.kz/data/objects/
```

**Время выполнения:** 2-3 минуты

---

## 🔧 НАСТРОЙКА GITHUB ACTIONS

### Шаг 1: Получить Railway Token

1. Откройте https://railway.app/account/tokens
2. Нажмите **"Create Token"**
3. Имя: `GitHub Actions`
4. Скопируйте токен

### Шаг 2: Добавить в GitHub Secrets

1. Откройте https://github.com/malsonvalentin-architector/rm-saas-platform/settings/secrets/actions
2. Нажмите **"New repository secret"**
3. Name: `RAILWAY_TOKEN`
4. Value: вставьте скопированный токен
5. Нажмите **"Add secret"**

### Шаг 3: Запустить workflow

1. Перейдите: https://github.com/malsonvalentin-architector/rm-saas-platform/actions
2. Выберите **"Reset Demo Data on Railway"**
3. Нажмите **"Run workflow"**
4. Выберите branch: **main**
5. Нажмите зелёную кнопку **"Run workflow"**

---

## 🎯 АВТОМАТИЧЕСКИЙ ЗАПУСК

GitHub Action запускается автоматически при:
- **Ручном запуске** (workflow_dispatch)
- **Push в main** который изменяет файл workflow

Для автоматического запуска каждую неделю, добавьте в `.github/workflows/reset_demo_data.yml`:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * 0'  # Каждое воскресенье в 2:00 UTC
```

---

## ❓ TROUBLESHOOTING

### Проблема: Railway CLI не работает на Windows

**Решение:**
Используйте GitHub Actions (Способ 1) - работает в облаке, не требует локальных инструментов.

### Проблема: "RAILWAY_TOKEN not found"

**Решение:**
Добавьте Railway Token в GitHub Secrets (см. "Настройка GitHub Actions" выше).

### Проблема: Workflow завершился с ошибкой

**Решение:**
1. Откройте https://github.com/malsonvalentin-architector/rm-saas-platform/actions
2. Кликните на failed workflow
3. Посмотрите логи
4. Напишите в чат - я помогу!

---

## 📚 ФАЙЛЫ В РЕПОЗИТОРИИ

```
.github/workflows/reset_demo_data.yml   - GitHub Actions workflow
auto_reset_demo.py                      - Python скрипт автосброса
data/management/commands/
  ├── reset_demo_data.py                - Management команда
  └── load_quality_demo.py              - Загрузка demo данных
```

---

## 🎉 ПРЕИМУЩЕСТВА

✅ **Не нужны локальные инструменты** (psql, Python)  
✅ **Работает через веб-интерфейс** GitHub  
✅ **Автоматизация** - один клик  
✅ **Надёжно** - выполняется в облаке  
✅ **Логи** - видно что происходит  

---

**Следующий шаг:** Настройте GitHub Actions и запустите workflow!

**Вопросы?** Напишите в чат! 🚀
