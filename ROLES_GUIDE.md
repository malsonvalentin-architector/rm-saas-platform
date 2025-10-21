# 👥 ProMonitor.kz - User Roles Guide

## 📊 Role Hierarchy

```
superadmin (RED badge)
    ↓
admin (BLUE badge)
    ↓
manager (YELLOW badge)
    ↓
client (GREEN badge)
```

---

## 🔑 Default Users & Credentials

### Production Users (After Phase 4.1 Fix)

| Email | Password | Role | Company | Badge Color | Access Level |
|-------|----------|------|---------|-------------|--------------|
| `superadmin@promonitor.kz` | `Super123!` | superadmin | *ALL companies* | 🔴 Red | Full system access |
| `admin@promonitor.kz` | `Vika2025` | admin | ProMonitor Admin | 🔵 Blue | Company administrator |
| `manager@promonitor.kz` | `Vika2025` | manager | ProMonitor Demo | 🟡 Yellow | Can create/edit |
| `client@promonitor.kz` | `Client123!` | client | ProMonitor Demo | 🟢 Green | Read-only |

---

## 🎭 Role Permissions Matrix

### Superadmin (superadmin)

**Badge:** 🔴 Red "Superadministrator"

**Permissions:**
- ✅ View: ALL companies
- ✅ Create: Everything
- ✅ Edit: Everything
- ✅ Delete: Everything
- ✅ Manage users: ALL users
- ✅ Manage companies: ALL companies
- ✅ Django Admin access: Yes

**Use Case:**
- System administrator
- Platform owner
- Technical support with full access

**Dashboard shows:**
- All objects from all companies
- All systems across all companies
- All alerts from all companies

---

### Admin (admin)

**Badge:** 🔵 Blue "Company Administrator"

**Permissions:**
- ✅ View: Own company only
- ✅ Create: Objects, systems, alerts
- ✅ Edit: Objects, systems, alerts
- ✅ Delete: Objects, systems, alerts
- ✅ Manage users: Own company users
- ❌ Manage companies: No
- ✅ Django Admin access: Yes (limited)

**Use Case:**
- Company administrator
- Main contact person
- Full control over company data

**Dashboard shows:**
- Objects from own company
- Systems from own company
- Alerts from own company

---

### Manager (manager)

**Badge:** 🟡 Yellow "Manager"

**Permissions:**
- ✅ View: Own company only
- ✅ Create: Objects, systems, alerts
- ✅ Edit: Objects, systems, alerts
- ❌ Delete: Nothing
- ❌ Manage users: No
- ❌ Manage companies: No
- ❌ Django Admin access: No

**Use Case:**
- Operations manager
- Facility manager
- Day-to-day operations

**Dashboard shows:**
- Objects from own company
- Systems from own company
- Alerts from own company

**UI Indicators:**
- "Создание" and "Редактирование" icons in dropdown
- No "Удаление" icon

---

### Client (client)

**Badge:** 🟢 Green "Client"

**Permissions:**
- ✅ View: Own company only
- ❌ Create: Nothing
- ❌ Edit: Nothing
- ❌ Delete: Nothing
- ❌ Manage users: No
- ❌ Manage companies: No
- ❌ Django Admin access: No

**Use Case:**
- External client
- Monitoring-only access
- Reports viewer

**Dashboard shows:**
- Objects from own company (read-only)
- Systems from own company (read-only)
- Alerts from own company (read-only)

**UI Indicators:**
- Info banner: "У вас режим только для чтения"
- Only "👁️ Только чтение" icon in dropdown
- No create/edit/delete buttons

---

## 🔧 Role Management

### Changing User Role (Django Admin)

1. Login as superadmin
2. Go to `/admin/`
3. Click "User profiles"
4. Find user
5. Change "Role" field
6. Save

### Assigning Company

1. Login as superadmin or admin
2. Go to `/admin/`
3. Click "User profiles"
4. Find user
5. Set "Company" field
6. Save

**Important:** 
- superadmin should have Company = NULL (sees all)
- Other roles MUST have a company assigned

---

## 🎨 Visual Indicators

### Navbar Dropdown

```
👤 user@email.com [ROLE BADGE]
   ↓
   Компания: Demo Company
   ────────────────────────────
   Права доступа:
   ➕ Создание ✏️ Редактирование 🗑️ Удаление
   (or)
   👁️ Только чтение
   ────────────────────────────
   🚪 Выйти
```

### Dashboard Banner (for client role)

```
ℹ️ Вы вошли как: Client | Компания: Demo Company
   👁️ У вас режим только для чтения. Вы не можете изменять данные.
```

---

## 🐛 Troubleshooting

### Issue: User shows wrong role badge

**Check:**
1. `data/models.py` - User_profile.role field
2. Database: SELECT role FROM data_user_profile WHERE email='...'
3. Clear browser cache

**Fix:**
```bash
python manage.py fix_admin_role
```

### Issue: admin@promonitor.kz shows as Superadministrator

**Cause:** Role is set to 'superadmin' instead of 'admin'

**Fix:**
```bash
python manage.py fix_admin_role
# or
python manage.py setup_default_users
```

### Issue: User can't see any data

**Check:**
1. User has company assigned?
2. Company has objects?
3. User role is correct?

**Fix:**
```python
# Django shell
user = User_profile.objects.get(email='...')
user.company = Company.objects.get(name='...')
user.save()
```

---

## 📋 Role Migration History

### Phase 4.1 (Current)

**Old roles → New roles:**
- `company_admin` → `admin`
- `operator` → `manager`
- `viewer` → `client`
- `superadmin` → `superadmin` (unchanged)

**Migration:** `data/migrations/0008_update_user_roles.py`

---

## 🔐 Security Notes

1. **superadmin should be restricted:**
   - Only for technical staff
   - Not for regular clients

2. **admin has full company control:**
   - Can delete critical data
   - Can manage users
   - Should be trusted personnel

3. **manager is safer:**
   - Can't delete data
   - Can't manage users
   - Good for operational staff

4. **client is safest:**
   - Read-only access
   - Perfect for external clients
   - No risk of accidental changes

---

## 📊 Statistics

**Current users by role:**
- superadmin: 1
- admin: 1
- manager: 1
- client: 1

**Total:** 4 default users

---

**Last Updated:** 2025-10-21  
**Version:** Phase 4.1  
**Status:** ✅ All roles working correctly
