# 🎮 PHASE 4.4: ACTUATORS & CONTROL - ИНСТРУКЦИЯ ПО ДЕПЛОЮ

## ✅ ШАГ 1: PUSH НА GITHUB

**Commit уже создан локально:**
```
Commit: 2cf5349
Message: 🎮 Phase 4.4 MVP: Actuators & Basic Control System
```

**Файлы изменены:**
- ✅ `data/models.py` - добавлены модели Actuator и ActuatorCommand
- ✅ `data/admin.py` - регистрация новых моделей
- ✅ `data/urls.py` - URL routing для актуаторов
- ✅ `data/views_actuators.py` - 3 view функции (list, control, history)
- ✅ `data/migrations/0012_phase_44_actuators.py` - миграция БД
- ✅ `templates/data/actuators_list.html` - главная страница управления
- ✅ `templates/data/actuator_history.html` - история команд
- ✅ `templates/data/object_list.html` - добавлена кнопка "Управление"
- ✅ `templates/data/all_systems.html` - добавлена кнопка "Управление"
- ✅ `templates/data/alerts_list.html` - добавлена кнопка "Управление"
- ✅ `data/management/commands/create_demo_actuators.py` - команда для демо данных

**Выполните push вручную через GitHub Desktop или командой:**

```bash
cd ~/promonitor
git push origin main
```

---

## ✅ ШАГ 2: RAILWAY AUTO-DEPLOY

Railway автоматически начнёт деплой после push.

**Процесс (5-7 минут):**
1. ⏳ Railway обнаружит новый commit
2. 🏗️ Build процесс (install dependencies)
3. 📦 Создание Docker образа
4. 🚀 Deploy на production
5. 🔄 Автоматический перезапуск приложения

**Отслеживание:**
- https://railway.app/project/[your-project-id]/deployments

---

## ✅ ШАГ 3: ЗАПУСК МИГРАЦИИ БД

После успешного деплоя выполните миграцию:

```bash
# В Railway Dashboard → Deployments → Latest → Shell
python manage.py migrate
```

**Ожидаемый результат:**
```
Running migrations:
  Applying data.0012_phase_44_actuators... OK
```

---

## ✅ ШАГ 4: СОЗДАНИЕ ДЕМО ДАННЫХ

Запустите команду создания тестовых актуаторов:

```bash
python manage.py create_demo_actuators
```

**Что будет создано:**
- 10 актуаторов разных типов (клапаны, реле, насосы, вентиляторы, моторы, нагреватели)
- 50-150 команд управления (история с метриками)
- Статус: 75% устройств онлайн
- Успешность команд: ~95%

---

## ✅ ШАГ 5: ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### 5.1. Главная страница управления
```
https://www.promonitor.kz/data/actuators/
```

**Проверьте:**
- ✅ Карточки статистики (всего, онлайн, активных, команды за 24ч)
- ✅ Фильтры (тип устройства, объект, статус, поиск)
- ✅ Список устройств с текущими значениями
- ✅ Кнопки "🎮 Управление" и "📊 История"

### 5.2. Управление устройством

**Бинарные устройства (реле, насосы, выключатели):**
- Нажмите "🎮 Управление"
- Должны появиться кнопки "⭕ ВЫКЛ" и "🟢 ВКЛ"
- Нажмите любую кнопку
- Значение должно обновиться
- Должно появиться сообщение "✅ Команда выполнена"

**Аналоговые устройства (клапаны, вентиляторы, моторы):**
- Нажмите "🎮 Управление"
- Должен появиться ползунок (0-100%)
- Перетащите ползунок
- Нажмите "✅ Выполнить команду"
- Значение должно обновиться

### 5.3. История команд
```
https://www.promonitor.kz/data/actuators/{id}/history/
```

**Проверьте:**
- ✅ Карточки статистики (всего команд, успешных, ошибок, успешность %)
- ✅ Таблица истории команд
- ✅ Информация о каждой команде (время, значение, пользователь, статус, отклик)

### 5.4. Навигация

**Проверьте кнопку "🎮 Управление" на страницах:**
- ✅ `/objects/` - страница объектов
- ✅ `/systems/` - страница систем
- ✅ `/alerts/` - страница тревог

---

## 📊 АРХИТЕКТУРА

### Модели:

```python
Actuator:
  - sys (ForeignKey → System)
  - name, description
  - actuator_type (valve/relay/pump/fan/motor/heater/switch/dimmer/cooler)
  - modbus_carel, register, carel_reg, register_type
  - min_value, max_value, default_value, current_value
  - last_command_at
  - is_active, is_online

ActuatorCommand:
  - actuator (ForeignKey → Actuator)
  - command_value
  - user (ForeignKey → User_profile)
  - executed_at
  - status (pending/success/failed/timeout)
  - response_time_ms
  - error_message, notes
  - source_ip
```

### URLs:

```
/data/actuators/                           - список устройств
/data/actuators/<id>/control/              - отправка команды (POST)
/data/actuators/<id>/history/              - история команд
```

### Views:

```python
actuators_list(request)          - главная страница с фильтрами
actuator_control(request, id)    - POST handler для команд
actuator_history(request, id)    - история команд устройства
```

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ (БУДУЩИЕ УЛУЧШЕНИЯ)

**После подтверждения работоспособности базовой версии можно добавить:**

1. **Реальная интеграция Modbus:**
   - Отправка команд на контроллеры CAREL
   - Чтение текущих значений
   - Обработка ошибок связи

2. **WebSocket для real-time обновлений:**
   - Обновление значений без перезагрузки страницы
   - Уведомления о командах других пользователей

3. **Права доступа:**
   - Роли: viewer (только просмотр), operator (управление), admin (все)
   - Аудит действий

4. **Сценарии управления:**
   - Групповые команды (управление несколькими устройствами)
   - Расписание (автоматическое выполнение в определённое время)
   - Условия (если температура > 25°C, то включить вентилятор)

5. **Графики и аналитика:**
   - История изменения значений
   - Частота использования
   - Среднее время отклика

---

## ❓ TROUBLESHOOTING

### Проблема: Миграция не применяется

**Решение:**
```bash
python manage.py showmigrations
python manage.py migrate data 0012_phase_44_actuators
```

### Проблема: Страница 404

**Проверьте:**
```bash
python manage.py show_urls | grep actuators
```

### Проблема: Ошибка импорта

**Проверьте:**
```bash
python manage.py check
```

### Проблема: Демо данные не создаются

**Проверьте наличие данных:**
```bash
python manage.py shell
>>> from data.models import Company, System
>>> Company.objects.count()
>>> System.objects.count()
```

---

## ✅ CHECKLIST ДЕПЛОЯ

- [ ] Git push выполнен успешно
- [ ] Railway deployment завершён (статус: Success)
- [ ] Миграция БД применена
- [ ] Демо данные созданы
- [ ] Главная страница `/actuators/` открывается
- [ ] Карточки статистики показывают корректные данные
- [ ] Фильтры работают
- [ ] Управление бинарными устройствами работает
- [ ] Управление аналоговыми устройствами работает
- [ ] История команд отображается
- [ ] Навигация работает на всех страницах
- [ ] Admin панель показывает новые модели

---

**Время выполнения всех шагов: ~15-20 минут**

**Готово к production! 🚀**
