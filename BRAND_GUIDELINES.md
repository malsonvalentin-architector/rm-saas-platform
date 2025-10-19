# 🎨 ProMonitor.kz - Brand Guidelines

**Версия:** 1.0  
**Дата:** 19 октября 2025

---

## 📖 О бренде

### Название
**ProMonitor.kz**

### Позиционирование
Профессиональная SaaS платформа для мониторинга и управления объектами в режиме реального времени.

### Целевая аудитория
- B2B сегмент (средний и крупный бизнес)
- Промышленные предприятия
- Управляющие компании
- Facility management компании
- Технологичные компании Казахстана

### Tone of Voice
- **Профессиональный** - серьёзный, надёжный
- **Технологичный** - современный, инновационный
- **Понятный** - без лишнего жаргона
- **Уверенный** - эксперт в своей области

---

## 🎨 Цветовая палитра

### Основные цвета

#### Primary Blue (Основной синий)
```
HEX: #0066CC
RGB: 0, 102, 204
CMYK: 100, 50, 0, 20
```
**Использование:** Логотип, кнопки CTA, заголовки, ссылки

#### Secondary Orange (Акцентный оранжевый)
```
HEX: #FF6600
RGB: 255, 102, 0
CMYK: 0, 60, 100, 0
```
**Использование:** Акценты, важные элементы, алерты, графики

### Дополнительные цвета

#### Dark Blue (Тёмно-синий)
```
HEX: #003366
RGB: 0, 51, 102
```
**Использование:** Футер, тёмные секции, текст на светлом фоне

#### Light Blue (Светло-синий)
```
HEX: #E6F2FF
RGB: 230, 242, 255
```
**Использование:** Фоны, карточки, hover состояния

#### Success Green (Успех)
```
HEX: #10B981
RGB: 16, 185, 129
```
**Использование:** Успешные операции, статус "активно"

#### Warning Yellow (Предупреждение)
```
HEX: #F59E0B
RGB: 245, 158, 11
```
**Использование:** Предупреждения, статус "требует внимания"

#### Error Red (Ошибка)
```
HEX: #EF4444
RGB: 239, 68, 68
```
**Использование:** Ошибки, критические алерты

### Нейтральные цвета

#### Dark Gray (Тёмно-серый) - Основной текст
```
HEX: #1F2937
RGB: 31, 41, 55
```

#### Medium Gray (Средне-серый) - Вторичный текст
```
HEX: #6B7280
RGB: 107, 114, 128
```

#### Light Gray (Светло-серый) - Границы, разделители
```
HEX: #E5E7EB
RGB: 229, 231, 235
```

#### White (Белый) - Фоны
```
HEX: #FFFFFF
RGB: 255, 255, 255
```

---

## 🔤 Типографика

### Основной шрифт (веб)
**Open Sans** или **Inter**
- Заголовки: 700 (Bold)
- Подзаголовки: 600 (SemiBold)
- Основной текст: 400 (Regular)
- Мелкий текст: 400 (Regular)

```css
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

### Размеры шрифтов

```css
h1: 48px / 3rem (Desktop), 36px / 2.25rem (Mobile)
h2: 36px / 2.25rem (Desktop), 28px / 1.75rem (Mobile)
h3: 28px / 1.75rem (Desktop), 24px / 1.5rem (Mobile)
h4: 24px / 1.5rem
h5: 20px / 1.25rem
h6: 18px / 1.125rem

Body: 16px / 1rem
Small: 14px / 0.875rem
Tiny: 12px / 0.75rem
```

### Межстрочный интервал
```
Заголовки: 1.2
Основной текст: 1.6
```

---

## 🎯 Логотип

### Варианты логотипа

#### 1. Полный логотип (Horizontal)
```
[📊 Icon] ProMonitor.kz
```
**Использование:** Шапка сайта, email подписи, презентации

#### 2. Компактный логотип (Icon + Short)
```
[📊] PM
```
**Использование:** Favicon, мобильные приложения, иконки

#### 3. Текстовый логотип
```
ProMonitor.kz
```
**Использование:** Документация, черно-белая печать

### Концепция иконки

Иконка представляет собой стилизованный график мониторинга:
- **Элементы:** Линия графика с точками
- **Форма:** Круг или квадрат с закруглёнными углами
- **Цвета:** Primary Blue + Secondary Orange
- **Стиль:** Минималистичный, современный

```
   /\    /\
  /  \  /  \
 /    \/    \___
```

### Защитное поле
Минимальное расстояние от логотипа до других элементов = высота буквы "o" в названии

### Минимальный размер
- Цифровой: 120px ширина
- Печать: 30mm ширина

### Недопустимо:
- ❌ Изменять пропорции
- ❌ Менять цвета (кроме white version)
- ❌ Добавлять эффекты (тени, градиенты)
- ❌ Поворачивать логотип
- ❌ Размещать на пёстром фоне

---

## 📐 UI Компоненты

### Кнопки

#### Primary Button
```css
background: #0066CC;
color: #FFFFFF;
border-radius: 8px;
padding: 12px 24px;
font-weight: 600;

hover {
  background: #0052A3;
}
```

#### Secondary Button
```css
background: transparent;
color: #0066CC;
border: 2px solid #0066CC;
border-radius: 8px;
padding: 12px 24px;

hover {
  background: #E6F2FF;
}
```

#### Danger Button
```css
background: #EF4444;
color: #FFFFFF;
border-radius: 8px;
padding: 12px 24px;
```

### Карточки
```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 12px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);

hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
```

### Формы
```css
input, textarea, select {
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  
  focus {
    border-color: #0066CC;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.1);
  }
}
```

---

## 💬 Слоганы

### Основной (русский)
**"Профессиональный мониторинг для профессионального бизнеса"**

### Основной (английский)
**"Professional monitoring for professional business"**

### Основной (казахский)
**"Кәсіби бизнес үшін кәсіби мониторинг"**

### Альтернативные слоганы:

**Русский:**
- "Полный контроль над вашими объектами"
- "Видьте больше. Контролируйте лучше."
- "Мониторинг нового поколения"
- "Технологии управления будущего"

**English:**
- "Complete control over your facilities"
- "See more. Control better."
- "Next-generation monitoring"
- "The future of facility management"

**Қазақша:**
- "Объектілеріңізді толық бақылау"
- "Көбірек көріңіз. Жақсырақ басқарыңыз."
- "Жаңа буын мониторингі"

---

## 📱 Иконография

### Стиль иконок
- **Тип:** Line icons (outline style)
- **Толщина линии:** 2px
- **Углы:** Закруглённые
- **Размер:** 24x24px базовый

### Рекомендуемая библиотека
- **Heroicons** (https://heroicons.com)
- **Feather Icons** (https://feathericons.com)
- **Font Awesome 5** (https://fontawesome.com)

### Основные иконки:

| Элемент | Иконка | Описание |
|---------|--------|----------|
| Компании | 🏢 | building / office-building |
| Объекты | 🏗️ | home / location-marker |
| Системы | ⚙️ | cog / adjustments |
| Пользователи | 👤 | user / users |
| Мониторинг | 📊 | chart-bar / trending-up |
| Уведомления | 🔔 | bell |
| Настройки | ⚙️ | cog |
| Выход | 🚪 | logout |

---

## 🌐 Web Design

### Сетка (Grid)
- **Колонок:** 12
- **Gutter:** 24px
- **Max-width:** 1280px
- **Breakpoints:**
  - Mobile: < 640px
  - Tablet: 640px - 1024px
  - Desktop: > 1024px

### Отступы (Spacing)
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
3xl: 64px
```

### Border Radius
```
sm: 4px
md: 8px
lg: 12px
xl: 16px
full: 9999px (круг)
```

### Тени (Shadows)
```css
sm: 0 1px 2px rgba(0,0,0,0.05)
md: 0 4px 6px rgba(0,0,0,0.1)
lg: 0 10px 15px rgba(0,0,0,0.1)
xl: 0 20px 25px rgba(0,0,0,0.15)
```

---

## 📄 Примеры использования

### Навигация
```
Фон: #FFFFFF
Текст: #1F2937
Логотип: Цветной
Кнопка: Primary Blue (#0066CC)
Граница: #E5E7EB (нижняя)
```

### Футер
```
Фон: #003366 (Dark Blue)
Текст: #FFFFFF
Ссылки: #E6F2FF (Light Blue)
Copyright: Medium Gray (#6B7280)
```

### Карточки компаний
```
Фон: #FFFFFF
Заголовок: Dark Gray (#1F2937)
Текст: Medium Gray (#6B7280)
Иконка: Primary Blue (#0066CC)
Статус: Success Green / Warning Yellow / Error Red
```

### Дашборд
```
Фон страницы: #F9FAFB
Карточки: #FFFFFF
Графики: Primary Blue + Secondary Orange
Sidebar: #F3F4F6
```

---

## 🎯 Примеры текстов

### Главная страница - Hero секция

**Заголовок (RU):**
"Профессиональный мониторинг объектов в режиме реального времени"

**Подзаголовок (RU):**
"ProMonitor.kz - современная платформа для управления и контроля промышленных объектов, систем HVAC и оборудования"

**CTA кнопка:** "Начать бесплатный пробный период"

---

**Заголовок (EN):**
"Professional facility monitoring in real-time"

**Подзаголовок (EN):**
"ProMonitor.kz - modern platform for managing and controlling industrial facilities, HVAC systems and equipment"

**CTA button:** "Start free trial"

---

### Email подписи

```
С уважением,
[Имя Фамилия]
[Должность]

ProMonitor.kz
Профессиональный мониторинг объектов
🌐 https://promonitor.kz
📧 [email]
📱 [телефон]

Made with ❤️ in Kazakhstan 🇰🇿
```

---

## 📊 Presentation Template

### Титульный слайд
```
[Крупный логотип по центру]

ProMonitor.kz
Профессиональный мониторинг объектов

[Дата/Название презентации]
```

### Контентный слайд
```
[Заголовок слайда - Primary Blue]

• Пункт списка
• Пункт списка
• Пункт списка

[Визуал/График]

[Футер: promonitor.kz | Страница X]
```

### Цветовая схема презентации
- Фон: White (#FFFFFF)
- Заголовки: Primary Blue (#0066CC)
- Текст: Dark Gray (#1F2937)
- Акценты: Secondary Orange (#FF6600)

---

## 🚀 Social Media

### Форматы изображений

- **Facebook Post:** 1200 x 630 px
- **Instagram Post:** 1080 x 1080 px
- **LinkedIn Post:** 1200 x 627 px
- **Twitter Post:** 1600 x 900 px
- **Stories (IG/FB):** 1080 x 1920 px

### Хэштеги
```
#ProMonitorKZ
#МониторингОбъектов
#УмныеЗдания
#SmartBuildings
#FacilityManagement
#IoTКазахстан
#DigitalKazakhstan
#MadeInKazakhstan
```

### Био (краткое описание)
```
ProMonitor.kz 🇰🇿
Профессиональный мониторинг объектов
📊 SaaS платформа для управления
🏢 Multi-tenant архитектура
🌐 promonitor.kz
```

---

## ✅ Чеклист использования бренда

- [ ] Используется правильный логотип
- [ ] Соблюдена цветовая палитра
- [ ] Применены правильные шрифты
- [ ] Соблюдены отступы и размеры
- [ ] Tone of Voice соответствует бренду
- [ ] Качество изображений высокое
- [ ] Адаптивность под разные устройства
- [ ] Accessibility стандарты соблюдены

---

## 📞 Контакты

**Вопросы по брендингу:**
brand@promonitor.kz

**Website:** https://promonitor.kz

---

**Версия:** 1.0  
**Дата последнего обновления:** 19 октября 2025  
**© 2025 ProMonitor.kz - Все права защищены**
