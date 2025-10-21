# 🚀 Quick Test Guide - После деплоя URL Fix

## ⏰ Ожидание деплоя (2-3 минуты)

Railway автоматически деплоит изменения с GitHub.

**Проверить статус:**
1. Откройте https://railway.app/dashboard
2. Найдите проект `rm-saas-platform`
3. Дождитесь статуса **"Success"** (зелёный)

---

## ✅ БЫСТРАЯ ПРОВЕРКА

### 1. Главная страница
```
https://www.promonitor.kz/
```
**Что проверить:**
- Navbar ссылка "Объекты" кликабельна
- Нет ошибок в консоли (F12)

### 2. Страница объектов
```
https://www.promonitor.kz/objects/
```
**Ожидаемый результат:**
- ✅ Список объектов загружается
- ✅ Не показывает 404 Page Not Found
- ✅ Для admin/manager: кнопка "Создать объект"

### 3. Детальный дашборд (выберите любой объект)
```
https://www.promonitor.kz/objects/1/
```
**Ожидаемый результат:**
- ✅ Детальная информация объекта
- ✅ Системы и датчики
- ✅ Real-time обновление (через 30 секунд)

---

## 🧪 ДЛЯ КАЖДОЙ РОЛИ

### Client (только просмотр)
**Login:** client@promonitor.kz / Client123!
- Видит список и детали
- НЕТ кнопок создать/редактировать/удалить

### Manager (может редактировать)
**Login:** manager@promonitor.kz / Vika2025
- Видит список и детали
- ЕСТЬ кнопки создать/редактировать/удалить
- Может создать новый объект

### Admin (полный доступ)
**Login:** admin@promonitor.kz / Vika2025
- Всё как у Manager
- Badge цвет: синий

### Superadmin (видит всё)
**Login:** superadmin@promonitor.kz / Super123!
- Видит объекты ВСЕХ компаний
- Badge цвет: красный
- Доступ к Django Admin

---

## 🐛 Если всё ещё 404

1. **Проверьте Railway logs:**
   - Railway Dashboard → Deployment → Deploy Logs
   - Найдите строку: `Starting Django server...`
   - Проверьте нет ли ошибок

2. **Hard refresh страницы:**
   - Chrome: `Ctrl + Shift + R` (Windows) или `Cmd + Shift + R` (Mac)
   - Очистите кэш браузера

3. **Проверьте URL без кэша:**
   - Откройте Incognito/Private mode
   - Зайдите на https://www.promonitor.kz/objects/

4. **Пришлите скриншоты:**
   - Railway deployment status
   - Browser error (F12 Console)
   - URL которые не работают

---

## 📋 CHECKLIST

- [ ] Railway deployment показывает "Success"
- [ ] `/` (главная) загружается
- [ ] `/objects/` показывает список (не 404)
- [ ] Navbar ссылка "Объекты" работает
- [ ] Детальный дашборд `/objects/1/` работает
- [ ] Real-time обновление работает (подождите 30 сек)
- [ ] Admin/Manager могут создать новый объект
- [ ] Client НЕ видит кнопки создать/редактировать

**Если ВСЕ галочки ✅ - Phase 4.2 работает!**

---

**Время создания:** 2025-10-21  
**Commit:** a7cc58c  
**Файлы изменены:** dashboard.html, object_dashboard.html
