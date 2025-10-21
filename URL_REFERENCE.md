# 🗺️ ProMonitor.kz - URL Reference Guide

## ✅ Working URLs (After Fix)

### 🔐 Authentication

| URL | Method | Description | Redirect |
|-----|--------|-------------|----------|
| `/login/` | GET | Login shortcut | → `/accounts/login/` |
| `/accounts/login/` | GET/POST | Django login page | After login → `/dashboard/` |
| `/accounts/logout/` | POST | Django logout (default) | → `/accounts/login/` |
| `/logout/` | GET | Custom logout | → `/accounts/login/` |
| `/` | GET | Homepage | If logged in → `/dashboard/`<br>If not → `/accounts/login/` |

### 📊 Dashboard & Home

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/` | GET | Homepage/Index | Optional |
| `/dashboard/` | GET | Main dashboard | ✅ Yes |

### 🏢 Objects & Data

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/objects/` | GET | List all objects | ✅ Yes |
| `/objects/<id>/` | GET | Object dashboard | ✅ Yes |
| `/sensors/<id>/history/` | GET | Sensor history | ✅ Yes |
| `/objects/<id>/realtime/` | GET/WS | Realtime data (WebSocket) | ✅ Yes |

### ⚙️ Admin

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/admin/` | GET/POST | Django Admin Panel | ✅ Yes (superadmin) |

### 📡 Telegram Integration

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/telegram/` | GET/POST | Telegram webhook/commands | Optional |

---

## 🚫 Common Errors & Solutions

### Error: 404 on `/login/`

**Symptom:**
```
Page not found (404)
"/app/login" does not exist
```

**Cause:** Old version without redirect

**Solution:** ✅ FIXED in commit `be93225`
- Added redirect: `/login/` → `/accounts/login/`
- Removed static() interference

### Error: Logout redirects to `/admin/`

**Symptom:** After clicking logout, redirected to Django admin page

**Cause:** Missing custom logout view

**Solution:** ✅ FIXED in commit `764bd67`
- Custom logout view: `/logout/`
- Always redirects to `/accounts/login/`

---

## 🔄 URL Resolution Order

Django checks URLs in this order:

1. ✅ `admin/` - Django Admin
2. ✅ `accounts/` - Django Auth (login, logout, password reset)
3. ✅ `login/` - Redirect to accounts/login/
4. ✅ `telegram/` - Telegram integration
5. ✅ `objects/`, `sensors/` - Data app URLs
6. ✅ `/`, `dashboard/`, `logout/` - Home app URLs
7. ❌ `^(?P<path>.*)$` - Static files catch-all (REMOVED)

---

## 🧪 Testing URLs

### Test Login Flow

```bash
# 1. Test login shortcut
curl -I https://www.promonitor.kz/login/
# Expected: 302 redirect to /accounts/login/

# 2. Test login page
curl -I https://www.promonitor.kz/accounts/login/
# Expected: 200 OK

# 3. Test dashboard (unauthenticated)
curl -I https://www.promonitor.kz/dashboard/
# Expected: 302 redirect to /accounts/login/

# 4. Test homepage
curl -I https://www.promonitor.kz/
# Expected: 302 redirect to /accounts/login/ (if not logged in)
```

### Test Logout Flow

```bash
# 1. Custom logout
curl -I https://www.promonitor.kz/logout/
# Expected: 302 redirect to /accounts/login/

# 2. Django default logout
curl -X POST https://www.promonitor.kz/accounts/logout/
# Expected: 302 redirect to /accounts/login/
```

---

## 📝 URL Naming Convention

### Named URLs (for {% url %} in templates)

```python
# Home app (namespace='home')
home:index          →  /
home:dashboard      →  /dashboard/
home:logout         →  /logout/

# Data app (namespace='data')
data:object_list         →  /objects/
data:object_dashboard    →  /objects/<id>/
data:sensor_history      →  /sensors/<id>/history/
data:realtime_data       →  /objects/<id>/realtime/

# Django Auth (no namespace)
login               →  /accounts/login/
logout              →  /accounts/logout/
password_reset      →  /accounts/password_reset/
password_change     →  /accounts/password_change/

# Custom redirects
login_redirect      →  /login/ (redirects to accounts/login)
```

### Usage in Templates

```html
<!-- Correct -->
<a href="{% url 'home:dashboard' %}">Dashboard</a>
<a href="{% url 'home:logout' %}">Logout</a>
<a href="{% url 'data:object_list' %}">Objects</a>

<!-- Also works (shortcut) -->
<a href="/login/">Login</a>
<a href="/dashboard/">Dashboard</a>
```

---

## 🔧 Troubleshooting

### Issue: 404 on custom URL

**Check:**
1. URL pattern order in `rm/urls.py`
2. Namespace in include()
3. App urls.py exists and is correct

### Issue: Redirect loop

**Check:**
1. LOGIN_URL setting
2. LOGIN_REDIRECT_URL setting
3. LOGOUT_REDIRECT_URL setting
4. @login_required decorator

### Issue: Static files not loading

**Check:**
1. WhiteNoise middleware enabled
2. collectstatic run
3. STATIC_URL and STATIC_ROOT configured
4. Don't use static() in production

---

## 📊 URL Statistics

- **Total URL patterns:** ~15
- **Authentication URLs:** 4
- **Dashboard URLs:** 2
- **Data/Object URLs:** 4
- **Admin URLs:** 1
- **Telegram URLs:** 1
- **Redirects:** 1

---

**Last Updated:** 2025-10-21  
**Version:** Phase 4.1  
**Status:** ✅ All URLs working correctly
