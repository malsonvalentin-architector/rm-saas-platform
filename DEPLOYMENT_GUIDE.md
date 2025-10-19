# 🚀 ПОЛНОЕ РУКОВОДСТВО ПО РАЗВЕРТЫВАНИЮ RM SaaS

**Дата:** 19 октября 2025  
**Версия:** 1.0 MVP  
**Время развертывания:** ~2 часа

---

## 📋 СОДЕРЖАНИЕ

1. [Предварительные требования](#предварительные-требования)
2. [Подготовка сервера](#подготовка-сервера)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка проекта](#настройка-проекта)
5. [Запуск с Docker](#запуск-с-docker)
6. [Настройка SSL](#настройка-ssl)
7. [Тестирование](#тестирование)
8. [Мониторинг](#мониторинг)
9. [Резервное копирование](#резервное-копирование)

---

## 🔧 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### Что вам понадобится:

1. **VPS сервер:**
   - Минимум: 2GB RAM, 1 CPU, 20GB SSD
   - Рекомендуется: 4GB RAM, 2 CPU, 40GB SSD
   - ОС: Ubuntu 20.04 LTS или 22.04 LTS

2. **Домен:**
   - Зарегистрированный домен (например: `rm-saas.com`)
   - Доступ к DNS настройкам

3. **Email аккаунт:**
   - Gmail с App Password (или другой SMTP)

4. **Опционально:**
   - Telegram Bot Token (для уведомлений)

---

## 🖥 ПОДГОТОВКА СЕРВЕРА

### Шаг 1: Подключение к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### Шаг 2: Обновление системы

```bash
apt update && apt upgrade -y
```

### Шаг 3: Создание пользователя

```bash
adduser deploy
usermod -aG sudo deploy
su - deploy
```

---

## 📦 УСТАНОВКА ЗАВИСИМОСТЕЙ

### Шаг 4: Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

### Шаг 5: Установка Git

```bash
sudo apt install git -y
```

---

## ⚙️ НАСТРОЙКА ПРОЕКТА

### Шаг 6: Клонирование проекта

```bash
cd /home/deploy
git clone YOUR_REPOSITORY_URL rm-saas
cd rm-saas
```

**Или загрузка архива:**

```bash
cd /home/deploy
# Загрузите архив rm_saas_mvp.tar.gz на сервер
tar -xzf rm_saas_mvp.tar.gz
cd rm
```

### Шаг 7: Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

**Обязательно измените:**

```env
# Безопасность
SECRET_KEY=your-super-secret-random-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# База данных
DB_NAME=rm_saas_production
DB_USER=rm_user
DB_PASSWORD=your-super-secure-db-password

# Email (Gmail пример)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# Суперпользователь
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@yourdomain.com
SUPERUSER_PASSWORD=your-secure-admin-password
```

**Как получить App Password для Gmail:**
1. Перейти: https://myaccount.google.com/security
2. Включить 2-Factor Authentication
3. Перейти: https://myaccount.google.com/apppasswords
4. Создать App Password для "Mail"
5. Использовать сгенерированный пароль в `EMAIL_HOST_PASSWORD`

### Шаг 8: Настройка DNS

Добавьте **A-записи** в настройках DNS вашего домена:

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

Проверка (может занять до 1 часа):
```bash
ping yourdomain.com
```

---

## 🐳 ЗАПУСК С DOCKER

### Шаг 9: Обновление nginx.conf

```bash
nano nginx.conf
```

Замените `yourdomain.com` на ваш реальный домен:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

### Шаг 10: Первый запуск (без SSL)

Временно закомментируйте SSL блок в `nginx.conf`:

```nginx
# ЗАКОММЕНТИРОВАТЬ ЭТО:
# listen 443 ssl http2;
# ssl_certificate /etc/letsencrypt/...;
# ssl_certificate_key /etc/letsencrypt/...;
```

И изменить redirect на:

```nginx
location / {
    proxy_pass http://web:8000;
    # ... остальное без изменений
}
```

### Шаг 11: Сборка и запуск

```bash
docker-compose build
docker-compose up -d
```

Проверка статуса:
```bash
docker-compose ps
```

Все сервисы должны быть в статусе **Up**.

### Шаг 12: Проверка логов

```bash
# Логи Django
docker-compose logs -f web

# Логи PostgreSQL
docker-compose logs -f db

# Логи Nginx
docker-compose logs -f nginx
```

### Шаг 13: Проверка доступа

Откройте в браузере:
```
http://yourdomain.com/admin/
```

Войдите с учётными данными из `.env`:
- Username: `admin` (или что вы указали)
- Password: (из `SUPERUSER_PASSWORD`)

---

## 🔒 НАСТРОЙКА SSL (HTTPS)

### Шаг 14: Остановка контейнеров

```bash
docker-compose down
```

### Шаг 15: Получение SSL сертификата

```bash
# Установка Certbot
sudo apt install certbot -y

# Получение сертификата
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com --email your-email@example.com --agree-tos
```

Сертификаты будут в:
```
/etc/letsencrypt/live/yourdomain.com/fullchain.pem
/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Шаг 16: Обновление docker-compose.yml

Добавьте volume для сертификатов в `nginx` сервис:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Шаг 17: Восстановление SSL в nginx.conf

Раскомментируйте SSL блок:

```nginx
listen 443 ssl http2;
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

### Шаг 18: Перезапуск с SSL

```bash
docker-compose up -d
```

Проверка:
```
https://yourdomain.com/admin/
```

### Шаг 19: Автообновление SSL

```bash
# Cron job для автообновления
sudo crontab -e

# Добавить строку:
0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

---

## ✅ ТЕСТИРОВАНИЕ

### Шаг 20: Проверочный список

- [ ] **Доступ к сайту:** https://yourdomain.com
- [ ] **Django Admin:** https://yourdomain.com/admin/
- [ ] **Super Admin:** https://yourdomain.com/superadmin/
- [ ] **Вход пользователя:** https://yourdomain.com/accounts/login/
- [ ] **Статические файлы загружаются** (CSS, JS, images)
- [ ] **Создание компании** через Django Admin
- [ ] **Создание пользователя** в компании
- [ ] **Создание объекта и системы**
- [ ] **Отправка email** (тестовое письмо)

### Команды для тестирования email:

```bash
docker-compose exec web python manage.py shell

# В shell:
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from RM SaaS',
    'noreply@yourdomain.com',
    ['your-email@example.com'],
    fail_silently=False,
)
```

---

## 📊 МОНИТОРИНГ

### Полезные команды:

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f web
docker-compose logs -f celery

# Использование ресурсов
docker stats

# Перезапуск сервиса
docker-compose restart web

# Полный рестарт
docker-compose down && docker-compose up -d

# Вход в контейнер
docker-compose exec web bash

# Миграции
docker-compose exec web python manage.py migrate

# Создание суперпользователя вручную
docker-compose exec web python manage.py createsuperuser

# Сборка статики
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 💾 РЕЗЕРВНОЕ КОПИРОВАНИЕ

### Backup базы данных:

```bash
# Создание backup
docker-compose exec db pg_dump -U rm_user rm_saas_production > backup_$(date +%Y%m%d).sql

# Восстановление из backup
docker-compose exec -T db psql -U rm_user rm_saas_production < backup_20251019.sql
```

### Автоматический backup (cron):

```bash
# Создать скрипт
nano /home/deploy/backup.sh

#!/bin/bash
cd /home/deploy/rm-saas
docker-compose exec -T db pg_dump -U rm_user rm_saas_production | gzip > /home/deploy/backups/db_$(date +%Y%m%d_%H%M%S).sql.gz
# Удалять старые (>30 дней)
find /home/deploy/backups -name "db_*.sql.gz" -mtime +30 -delete

# Сделать исполняемым
chmod +x /home/deploy/backup.sh

# Добавить в cron (каждый день в 2:00)
sudo crontab -e
0 2 * * * /home/deploy/backup.sh
```

---

## 🆘 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Контейнер не запускается

```bash
docker-compose logs web
docker-compose logs db
```

### Проблема: База данных не подключается

```bash
# Проверка .env
cat .env | grep DB_

# Проверка подключения
docker-compose exec web python manage.py dbshell
```

### Проблема: Статика не загружается

```bash
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart nginx
```

### Проблема: Email не отправляется

```bash
# Проверка настроек
docker-compose exec web python manage.py shell
from django.conf import settings
print(settings.EMAIL_HOST_USER)
```

---

## 🎉 ГОТОВО!

Ваша RM SaaS платформа развёрнута и работает!

**Доступ:**
- 🌐 Сайт: https://yourdomain.com
- 🔧 Django Admin: https://yourdomain.com/admin/
- 👑 Super Admin: https://yourdomain.com/superadmin/

**Следующие шаги:**
1. Создайте первую компанию через Django Admin
2. Создайте пользователей для компании
3. Настройте тарифные планы
4. Добавьте объекты и системы
5. Настройте правила тревог

**Поддержка:**
- Email: admin@yourdomain.com
- Документация: /home/deploy/rm-saas/docs/

---

**Успешного развёртывания! 🚀**
