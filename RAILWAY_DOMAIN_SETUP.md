# 🌐 Railway Domain Setup для ProMonitor.kz

**Домен:** promonitor.kz  
**Дата:** 19 октября 2025  
**Статус:** Готово к настройке

---

## 🎉 ДОМЕН КУПЛЕН!

Отлично! Теперь настроим promonitor.kz на Railway.

---

## 📋 ШАГ 1: Добавление домена в Railway

### 1.1 Откройте Railway Dashboard
1. Перейдите на https://railway.app
2. Войдите в свой аккаунт
3. Откройте проект **web-production-19bde**

### 1.2 Добавьте Custom Domain
1. Кликните на ваш **web service**
2. Перейдите на вкладку **"Settings"**
3. Найдите секцию **"Domains"**
4. Нажмите **"Add Custom Domain"**
5. Введите: `promonitor.kz`
6. Нажмите **"Add Domain"**

### 1.3 Добавьте WWW субдомен
Повторите процесс для:
- `www.promonitor.kz`

---

## 📋 ШАГ 2: DNS настройка в KazNIC

Railway покажет вам DNS записи, которые нужно добавить. Обычно это:

### Вариант A: CNAME Records (рекомендуется)

**Для www субдомена:**
```
Type: CNAME
Name: www
Value: [your-railway-project].up.railway.app
TTL: 3600 (или оставьте по умолчанию)
```

**Для корневого домена (@ или promonitor.kz):**

Railway может предоставить один из вариантов:

#### Вариант 1: CNAME (если поддерживается)
```
Type: CNAME
Name: @
Value: [your-railway-project].up.railway.app
TTL: 3600
```

#### Вариант 2: A Record
```
Type: A
Name: @
Value: [Railway IP address]
TTL: 3600
```

**Важно:** Railway покажет точные значения в интерфейсе!

---

## 📋 ШАГ 3: Добавление DNS записей в KazNIC

### 3.1 Войдите в панель управления доменом
1. Откройте https://nic.kz
2. Войдите в личный кабинет
3. Найдите домен **promonitor.kz**
4. Перейдите в управление DNS

### 3.2 Добавьте записи

**Скопируйте точные значения из Railway dashboard!**

#### Пример (ваши значения будут другими):
```
Type: CNAME
Host: www
Value: web-production-19bde.up.railway.app
TTL: 3600

Type: A (или CNAME если поддерживается)
Host: @
Value: [IP или CNAME от Railway]
TTL: 3600
```

### 3.3 Сохраните изменения
После добавления записей нажмите **"Сохранить"** или **"Apply"**

---

## ⏰ ШАГ 4: Ожидание DNS propagation

### Время ожидания:
- **Минимум:** 5-15 минут
- **Обычно:** 1-4 часа
- **Максимум:** 24-48 часов

### Как проверить:

#### Вариант 1: Командная строка
```bash
# Проверка CNAME
nslookup www.promonitor.kz

# Проверка A record
nslookup promonitor.kz

# Альтернативная проверка
dig promonitor.kz
dig www.promonitor.kz
```

#### Вариант 2: Онлайн инструменты
- https://www.whatsmydns.net
- https://dnschecker.org

Введите `promonitor.kz` и проверьте распространение по миру.

---

## 🔒 ШАГ 5: SSL сертификат (автоматически)

Railway автоматически настроит **Let's Encrypt SSL** сертификат.

### Что происходит:
1. Вы добавляете домен в Railway ✅
2. Вы настраиваете DNS записи ✅
3. DNS propagation завершается ⏰
4. Railway **автоматически** генерирует SSL сертификат 🔒
5. Ваш сайт доступен через HTTPS ✅

### Время генерации SSL:
- **Обычно:** 5-15 минут после DNS propagation
- **Максимум:** 1-2 часа

### Проверка SSL:
Откройте в браузере:
```
https://promonitor.kz
https://www.promonitor.kz
```

Должен быть 🔒 зелёный замочек!

---

## ✅ ШАГ 6: Проверка работы

### 6.1 Откройте сайт
Перейдите на:
- https://promonitor.kz
- https://www.promonitor.kz

### 6.2 Проверьте функционал
- [ ] Главная страница загружается
- [ ] Форма логина работает
- [ ] Вход с admin@promonitor.kz / admin123
- [ ] Меню отображается
- [ ] Footer показывает "ProMonitor.kz"

### 6.3 Проверьте редирект HTTP → HTTPS
Railway автоматически настраивает редирект:
- `http://promonitor.kz` → `https://promonitor.kz` ✅

---

## 🔧 Troubleshooting

### Проблема 1: "This site can't be reached"

**Причина:** DNS записи ещё не распространились

**Решение:**
1. Подождите 1-4 часа
2. Проверьте DNS на https://www.whatsmydns.net
3. Убедитесь что DNS записи добавлены правильно в KazNIC

---

### Проблема 2: "SSL certificate error"

**Причина:** SSL сертификат ещё генерируется

**Решение:**
1. Подождите 15-30 минут
2. Проверьте в Railway Settings → Domains
3. Должна быть зелёная галочка ✅ рядом с доменом

---

### Проблема 3: "DisallowedHost at /"

**Причина:** Домен не добавлен в ALLOWED_HOSTS

**Решение:**
Уже исправлено в коммите! `rm/settings.py` содержит:
```python
ALLOWED_HOSTS = [
    'promonitor.kz',
    'www.promonitor.kz',
    'web-production-19bde.up.railway.app',
    'localhost',
    '127.0.0.1',
]
```

Если проблема осталась - проверьте что код задеплоен на Railway.

---

### Проблема 4: Домен работает, но старый URL тоже

**Это нормально!** 

Оба домена будут работать:
- ✅ https://promonitor.kz (основной)
- ✅ https://www.promonitor.kz (WWW)
- ✅ https://web-production-19bde.up.railway.app (Railway subdomain)

Railway subdomain оставьте для тестирования и бэкапа.

---

## 📧 ШАГ 7: Настройка Email (опционально, но рекомендуется)

### После настройки домена рекомендуем:

1. **Создать email адреса:**
   - admin@promonitor.kz (уже указан в коде)
   - support@promonitor.kz
   - info@promonitor.kz

2. **Выбрать email провайдер:**
   
   **Яндекс 360 (рекомендуем):**
   - Бесплатно для малого бизнеса
   - https://360.yandex.ru
   - Инструкция: https://yandex.ru/support/business/add-domain.html

   **Mail.ru для бизнеса:**
   - Бесплатно
   - https://biz.mail.ru

   **Google Workspace:**
   - $6/месяц
   - https://workspace.google.com

3. **Настроить MX записи в KazNIC**
   
   Email провайдер (например, Яндекс) даст вам MX записи типа:
   ```
   Type: MX
   Priority: 10
   Value: mx.yandex.net
   ```

4. **Обновить Django settings**
   
   После настройки email добавьте в `rm/settings.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.yandex.ru'  # Для Яндекс
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'admin@promonitor.kz'
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
   ```

   И добавьте в Railway environment variables:
   ```
   EMAIL_PASSWORD=ваш_пароль_от_email
   ```

---

## 🎯 Итоговый чеклист

### Railway:
- [ ] Добавлен домен `promonitor.kz` в Railway
- [ ] Добавлен домен `www.promonitor.kz` в Railway
- [ ] Скопированы DNS записи из Railway

### KazNIC:
- [ ] Добавлены CNAME/A записи для promonitor.kz
- [ ] Добавлена CNAME запись для www.promonitor.kz
- [ ] Сохранены изменения

### Ожидание:
- [ ] DNS propagation завершился (1-4 часа)
- [ ] SSL сертификат сгенерирован (15-30 минут)

### Проверка:
- [ ] https://promonitor.kz открывается ✅
- [ ] https://www.promonitor.kz открывается ✅
- [ ] SSL сертификат активен 🔒
- [ ] Логин работает
- [ ] Footer показывает правильное название

---

## 🚀 Что дальше?

После успешной настройки домена:

1. ✅ **Обновите социальные сети**
   - LinkedIn, Instagram, Facebook
   - Везде укажите promonitor.kz

2. ✅ **Настройте email**
   - Создайте admin@promonitor.kz
   - Настройте SMTP в Django

3. ✅ **Создайте логотип**
   - Закажите на Fiverr ($50-200)
   - Добавьте в header сайта

4. ✅ **Google Analytics**
   - Добавьте tracking code
   - Мониторьте посещаемость

5. ✅ **Google Search Console**
   - Добавьте сайт
   - Подтвердите владение доменом
   - Отправьте sitemap

---

## 📞 Поддержка

**Вопросы по настройке домена:**

**Railway Support:**
- https://railway.app/help
- Telegram: @railwayapp

**KazNIC Support:**
- https://nic.kz
- Email: support@nic.kz
- Телефон: +7 (727) 258-07-78

---

## ✅ Готово!

После выполнения всех шагов ваша платформа **ProMonitor.kz** будет доступна по адресу:

🌐 **https://promonitor.kz**

**Поздравляем с запуском!** 🎉

---

**Версия:** 1.0  
**Дата:** 19 октября 2025  
**© 2025 ProMonitor.kz**
