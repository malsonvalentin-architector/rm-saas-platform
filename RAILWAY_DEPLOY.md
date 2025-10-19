# 🚂 РАЗВЁРТЫВАНИЕ НА RAILWAY.APP

**Время развёртывания:** 15-30 минут  
**Стоимость:** $5 бесплатно, потом ~$5-20/мес

---

## 📋 ЧТО ТАКОЕ RAILWAY?

Railway.app - это современная PaaS платформа (Platform as a Service), которая:
- ✅ Автоматически разворачивает приложения из Git
- ✅ Предоставляет PostgreSQL базу данных
- ✅ Даёт бесплатный домен `*.railway.app`
- ✅ Автоматический SSL/HTTPS
- ✅ Простой интерфейс управления
- ✅ Логи в реальном времени

**Идеально для тестирования и MVP!**

---

## 🚀 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Создать аккаунт на Railway

1. Перейти: https://railway.app/
2. Нажать **"Start a New Project"**
3. Войти через **GitHub** (рекомендуется)

---

### ШАГ 2: Создать GitHub репозиторий

**Вариант A: Через веб-интерфейс GitHub (проще)**

1. Открыть https://github.com/new
2. Название: `rm-saas-platform` (или любое)
3. Выбрать: **Private** (приватный репозиторий)
4. НЕ добавлять README, .gitignore, license
5. Нажать **"Create repository"**

**Вариант B: Я создам команды для терминала**

Если нужны команды для загрузки кода в GitHub - скажи, я дам!

---

### ШАГ 3: Загрузить код на GitHub

**Если ты на своём компьютере:**

```bash
# 1. Распаковать архив
tar -xzf rm_saas_complete_production_ready.tar.gz
cd rm

# 2. Инициализация Git
git init
git add .
git commit -m "Initial commit: RM SaaS Platform MVP"

# 3. Привязать к GitHub (замени на свой URL)
git remote add origin https://github.com/YOUR_USERNAME/rm-saas-platform.git
git branch -M main
git push -u origin main
```

**Или я могу:**
- Создать репозиторий за тебя (нужен GitHub token)
- Загрузить код напрямую

---

### ШАГ 4: Развернуть на Railway

1. **В Railway нажать: "Deploy from GitHub repo"**

2. **Выбрать репозиторий:** `rm-saas-platform`

3. **Railway автоматически:**
   - Обнаружит Python проект
   - Установит зависимости из `requirements_railway.txt`
   - Запустит миграции
   - Соберёт статические файлы

4. **Дождаться деплоя** (2-5 минут)

---

### ШАГ 5: Добавить PostgreSQL базу данных

1. В проекте Railway нажать **"+ New"**
2. Выбрать **"Database" → "PostgreSQL"**
3. Railway автоматически:
   - Создаст базу данных
   - Установит переменную `DATABASE_URL`
   - Подключит к вашему приложению

4. **Перезапустить приложение** (кнопка "Restart")

---

### ШАГ 6: Настроить переменные окружения

В Railway перейти в **"Variables"** и добавить:

```env
# Обязательные
DJANGO_SETTINGS_MODULE=rm.settings_railway
SECRET_KEY=your-random-secret-key-generate-new-one
DEBUG=False

# Опционально (для email)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Как сгенерировать SECRET_KEY:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### ШАГ 7: Создать суперпользователя

1. В Railway открыть **проект → "Settings" → "Command"**

2. Запустить команду:
```bash
python manage.py createsuperuser
```

3. Ввести:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `ваш_пароль`

---

### ШАГ 8: Открыть приложение! 🎉

1. Railway покажет домен: `your-project.railway.app`

2. Открыть в браузере:
   - 🌐 Главная: `https://your-project.railway.app/`
   - 🔧 Django Admin: `https://your-project.railway.app/admin/`
   - 👑 Super Admin: `https://your-project.railway.app/superadmin/`

3. Войти с учётными данными суперпользователя

---

## ✅ ПРОВЕРОЧНЫЙ СПИСОК

После деплоя проверь:

- [ ] Сайт открывается по домену
- [ ] Django Admin доступен `/admin/`
- [ ] Можешь войти как суперпользователь
- [ ] Super Admin панель работает `/superadmin/`
- [ ] Статические файлы загружаются (CSS, JS)
- [ ] Можешь создать компанию
- [ ] Можешь создать пользователя в компании
- [ ] Можешь создать объект и систему

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: "Application Error"

**Решение:**
1. Открыть **"Deployments" → последний deploy → "View Logs"**
2. Найти ошибку в логах
3. Обычно это:
   - Не установлена переменная `DJANGO_SETTINGS_MODULE`
   - Не добавлена база данных PostgreSQL

### Проблема: "Static files not found"

**Решение:**
1. Проверить что установлен `whitenoise` в requirements
2. В логах должно быть: `Collecting static files...`
3. Перезапустить приложение

### Проблема: "Database connection error"

**Решение:**
1. Проверить что добавлена PostgreSQL база
2. Проверить переменную `DATABASE_URL` в Variables
3. Перезапустить приложение

---

## 💰 СТОИМОСТЬ RAILWAY

**Бесплатный план:**
- $5 бесплатно каждый месяц
- Достаточно для тестирования
- ~500 часов работы

**После исчерпания бесплатного:**
- ~$5-20/мес в зависимости от использования
- PostgreSQL: ~$5/мес
- Приложение: ~$5-10/мес

---

## 🔄 КАК ОБНОВЛЯТЬ КОД

После изменений в коде:

```bash
git add .
git commit -m "Updated feature X"
git push
```

Railway **автоматически** развернёт новую версию!

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После успешного деплоя на Railway:

1. ✅ Протестировать все функции
2. ✅ Создать тестовые компании и пользователей
3. ✅ Проверить работу подписок
4. ✅ Доработать что нужно
5. ✅ Потом перенести на DigitalOcean для production

---

## 🆘 НУЖНА ПОМОЩЬ?

Если что-то не работает - напиши мне:
- Скриншот ошибки
- Логи из Railway
- Что именно не работает

Я помогу разобраться! 🚀

---

**Удачи с развёртыванием!** 🎉
