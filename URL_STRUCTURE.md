# ProMonitor URL Structure

## Основная структура (Production)

### 1. Главная страница (Landing)
- **URL:** `https://www.promonitor.kz/`
- **Описание:** Главная страница сайта с информацией о продукте
- **Элементы:** Кнопки "Войти" и "Регистрация"
- **Статус:** 🔄 В разработке

### 2. Аутентификация
- **Login:** `https://www.promonitor.kz/accounts/login/`
- **Logout:** `https://www.promonitor.kz/accounts/logout/`
- **Admin Login:** `https://www.promonitor.kz/admin/login/`
- **Редирект:** `/login/` → `/accounts/login/` (автоматически)

### 3. Dashboard (Основное приложение)

#### Главная страница dashboard
- **URL:** `https://www.promonitor.kz/dashboard/`
- **View:** `views_v2.dashboard_main_professional`
- **Template:** `templates/dashboard/v2/main_professional.html`
- **Описание:** Professional monitoring dashboard с honeycomb visualization
- **Статус:** ✅ Работает

#### Страницы мониторинга
| Страница | URL | View | Статус |
|----------|-----|------|--------|
| Buildings | `/dashboard/buildings/` | `views_v2_pages.buildings_list` | ✅ Работает |
| Sensors | `/dashboard/sensors/` | `views_v2_pages.sensors_list` | ✅ Работает |
| Alerts | `/dashboard/alerts/` | `/dashboard/alerts/` | `views_v2_pages.alerts_list` | ✅ Работает |

#### Аналитика и отчеты
| Страница | URL | View | Статус |
|----------|-----|------|--------|
| Reports | `/dashboard/reports/` | `views_v2_pages.reports_page` | ⏳ Coming Soon |
| Analytics | `/dashboard/analytics/` | `views_v2_pages.analytics_page` | ⏳ Coming Soon |

#### Системные настройки
| Страница | URL | View | Статус |
|----------|-----|------|--------|
| Settings | `/dashboard/settings/` | `views_v2_pages.settings_page` | ⏳ Coming Soon |
| Users | `/dashboard/users/` | `views_v2_pages.users_page` | ⏳ Coming Soon |

### 4. Emulator (Отдельный сервис)
- **URL:** `https://emulator.promonitor.kz/`
- **Описание:** Modbus TCP emulator для тестирования
- **Статус:** ✅ Работает
- **Примечание:** Не трогаем, работает отдельно

## Legacy URLs (Redirects)

Старые URL автоматически перенаправляются на новые:

| Старый URL | Новый URL | Redirect Type |
|-----------|-----------|---------------|
| `/dashboard/v2/` | `/dashboard/` | 301 Permanent |
| `/dashboard/main/` | `/dashboard/` | 301 Permanent |
| `/dashboard/v2/buildings/` | `/dashboard/buildings/` | N/A (обновлены ссылки) |
| `/dashboard/v2/sensors/` | `/dashboard/sensors/` | N/A (обновлены ссылки) |
| `/dashboard/v2/alerts/` | `/dashboard/alerts/` | N/A (обновлены ссылки) |
| `/dashboard/v2/reports/` | `/dashboard/reports/` | N/A (обновлены ссылки) |
| `/dashboard/v2/analytics/` | `/dashboard/analytics/` | N/A (обновлены ссылки) |
| `/dashboard/v2/settings/` | `/dashboard/settings/` | N/A (обновлены ссылки) |
| `/dashboard/v2/users/` | `/dashboard/users/` | N/A (обновлены ссылки) |

## URL Configuration Files

### 1. Main URLs (`rm/urls.py`)
```python
# Dashboard - Clean Structure
path('dashboard/', include(('home.urls_v2', 'dashboard_v2'))),

# Legacy redirects
path('dashboard/v2/', RedirectView.as_view(url='/dashboard/', permanent=True)),
path('dashboard/main/', RedirectView.as_view(url='/dashboard/', permanent=True)),
```

### 2. Dashboard URLs (`home/urls_v2.py`)
```python
app_name = 'dashboard_v2'

urlpatterns = [
    path('', views_v2.dashboard_main_professional, name='main'),
    path('buildings/', views_v2_pages.buildings_list, name='buildings'),
    path('sensors/', views_v2_pages.sensors_list, name='sensors'),
    path('alerts/', views_v2_pages.alerts_list, name='alerts'),
    # ... и т.д.
]
```

## Navigation Structure

Sidebar navigation использует следующую структуру:

### MAIN Section
- Dashboard (`/dashboard/`)
- Buildings (`/dashboard/buildings/`)
- Sensors (`/dashboard/sensors/`)
- Alerts (`/dashboard/alerts/`)

### ANALYTICS Section
- Reports (`/dashboard/reports/`)
- Analytics (`/dashboard/analytics/`)

### SYSTEM Section
- Settings (`/dashboard/settings/`)
- Users (`/dashboard/users/`)

### TOOLS Section
- Modbus Emulator (external: `https://emulator.promonitor.kz/`)

## API Endpoints

### Dashboard API
- Honeycomb Data: `/dashboard/api/honeycomb-data/`
- Dashboard Stats: `/dashboard/api/stats/`
- User Theme: `/dashboard/api/v2/user/theme`

### AI Assistant API
- Chat: `/dashboard/api/v2/ai/chat`
- Rate Message: `/dashboard/api/ai-rate/`
- History: `/dashboard/api/ai-history/`
- Clear History: `/dashboard/api/ai-clear/`
- Status: `/dashboard/api/ai-status/`
- Quick Analysis: `/dashboard/api/ai-analysis/`
- Suggestions: `/dashboard/api/ai-suggestions/`

## Примечания

1. **Все URL теперь короткие и чистые** - убрали `/v2/` из структуры
2. **SEO-friendly** - простые и понятные адреса
3. **Backward compatibility** - старые URL редиректятся автоматически
4. **Namespace:** Все dashboard routes используют namespace `dashboard_v2`
5. **Active class:** Автоматически устанавливается на текущей странице в sidebar

## Обновление от: 2025-10-25
