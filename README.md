# 🚀 ProMonitor.kz - Профессиональный мониторинг объектов

**ProMonitor.kz** - это современная SaaS платформа для удалённого мониторинга и управления объектами, системами и оборудованием в режиме реального времени.

## 📋 О проекте

**ProMonitor.kz** - профессиональное решение для мониторинга промышленных объектов, систем HVAC, энергоснабжения и другого оборудования через удобный веб-интерфейс.

### ✨ Основные возможности:

- 🏢 **Multi-tenant архитектура** - полная изоляция данных между компаниями
- 👥 **Гибкая система ролей** - company_admin, operator, viewer
- 📊 **Мониторинг в реальном времени** - актуальные данные с объектов
- 🏗️ **Управление объектами** - здания, помещения, территории
- ⚙️ **Управление системами** - HVAC, энергоснабжение, безопасность
- 📈 **Тарифные планы** - гибкая система подписок для бизнеса
- 📧 **Email уведомления** - автоматические алерты и отчёты
- 👑 **Super Admin панель** - централизованное управление клиентами
- 🇰🇿 **Создано в Казахстане** - учитывает местную специфику

## 🚀 Быстрый старт

### Railway Deployment (рекомендуется для начала)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/malsonvalentin-architector/rm-saas-platform.git
cd rm-saas-platform

# 2. Разверните на Railway
# - Зарегистрируйтесь на https://railway.app
# - Deploy from GitHub repo
# - Добавьте PostgreSQL plugin
# - Готово за 5 минут!
```

**Текущий деплой:** https://web-production-19bde.up.railway.app

### Локальная разработка

```bash
# 1. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Настройте базу данных
python manage.py migrate

# 4. Создайте superuser
python manage.py create_superuser

# 5. Запустите сервер
python manage.py runserver
```

**Доступ:** http://localhost:8000

**Credentials по умолчанию:**
- Email: admin@example.com
- Password: admin123

## 🏗️ Архитектура

### Технологический стек:

- **Backend:** Django 1.11.29 (Python 3.6)
- **Database:** PostgreSQL 12+
- **Web Server:** Gunicorn
- **Task Queue:** Celery + Redis
- **Frontend:** Bootstrap 3, jQuery
- **Deployment:** Railway, Docker-ready

### Основные модели:

#### 🏢 Company (Компания)
- Multi-tenant изоляция данных
- Тарифные планы и подписки
- White-label кастомизация (logo, цвета)
- Telegram интеграция

#### 👤 User_profile (Пользователь)
- Аутентификация через email
- Привязка к компании
- Роли: company_admin / operator / viewer
- Email и Telegram уведомления

#### 🏗️ Obj (Объект)
- Здания, помещения, территории
- Адрес и геолокация
- Привязка к компании
- История изменений

#### ⚙️ System (Система)
- HVAC системы
- Энергоснабжение
- Безопасность
- Статус и мониторинг

## 📚 Документация

### Доступные гайды:

- 📖 [RESTORATION_GUIDE.md](docs/RESTORATION_GUIDE.md) - Полное руководство по восстановлению
- 🚀 [QUICK_START.md](docs/QUICK_START.md) - Быстрая справка
- 🔧 [TECHNICAL_CHANGELOG.md](docs/TECHNICAL_CHANGELOG.md) - История изменений
- 🗃️ [RAILWAY_POSTGRESQL_SETUP.md](docs/RAILWAY_POSTGRESQL_SETUP.md) - Настройка PostgreSQL
- ✅ [DEPLOYMENT_FINAL_CHECKLIST.md](docs/DEPLOYMENT_FINAL_CHECKLIST.md) - Чеклист деплоя

## 🔑 Основные URL

### Пользовательские:
- `/` - Главная страница
- `/accounts/login/` - Вход
- `/accounts/register/` - Регистрация
- `/data/` - Список пользователей/объектов

### Админские:
- `/admin/` - Django Admin
- `/superadmin/` - Super Admin панель (Multi-Tenancy)

## 🛠️ Команды разработки

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание superuser
python manage.py create_superuser

# Сбор static файлов
python manage.py collectstatic --noinput

# Запуск Celery worker (в отдельном терминале)
celery -A rm worker -l info

# Запуск Celery beat (в отдельном терминале)
celery -A rm beat -l info
```

## 🌐 Deployment

### Railway (Production):

```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Войдите
railway login

# 3. Инициализируйте проект
railway init

# 4. Добавьте PostgreSQL
railway add --plugin postgresql

# 5. Деплой
git push railway main
```

### Environment Variables:

```bash
# Автоматически устанавливаются Railway:
PGDATABASE=...
PGUSER=...
PGPASSWORD=...
PGHOST=...
PGPORT=5432

# Рекомендуется добавить:
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=promonitor.kz,www.promonitor.kz
```

## 📊 Статус проекта

- ✅ **Production Ready** - Готово к использованию
- ✅ **PostgreSQL** - Persistent storage настроен
- ✅ **Auto Deploy** - CI/CD через Railway
- ✅ **Documentation** - Полная документация
- ✅ **Multi-Tenancy** - Изоляция данных работает

**Версия:** 1.0.0  
**Последнее обновление:** 19 октября 2025

## 🚀 Roadmap

### Краткосрочные цели (1-2 месяца):
- [ ] Восстановить функционал графиков (data visualization)
- [ ] Настроить Celery/Redis для background tasks
- [ ] Добавить REST API
- [ ] Создать мобильное приложение (PWA)
- [ ] Интегрировать платёжную систему

### Долгосрочные цели (3-6 месяцев):
- [ ] Миграция на Django 4.2 LTS
- [ ] AI/ML для predictive maintenance
- [ ] Multi-language support (KZ/RU/EN)
- [ ] Интеграция с IoT устройствами
- [ ] Advanced analytics и reporting

## 🤝 Поддержка

**Website:** https://promonitor.kz  
**Email:** admin@promonitor.kz  
**GitHub:** https://github.com/malsonvalentin-architector/rm-saas-platform

## 📄 Лицензия

Proprietary - Все права защищены © 2025 ProMonitor.kz

---

**Made with ❤️ in Kazakhstan 🇰🇿**

Профессиональный мониторинг для профессионального бизнеса.
