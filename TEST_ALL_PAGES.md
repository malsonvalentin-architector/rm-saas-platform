# ✅ ТЕСТИРОВАНИЕ ВСЕХ СТРАНИЦ - Phase 2

**Цель:** Убедиться что все 5 страниц работают после deployment commit `ca25cc6`

---

## 🔐 ШАГИ ТЕСТИРОВАНИЯ

### **1. Login (Required First)**
**URL:** https://www.promonitor.kz/accounts/login/

**Test Credentials:**
```
Email: admin@promonitor.kz
Password: Vika2025
```

**Expected Result:** Успешный вход, редирект на dashboard

---

### **2. Dashboard Overview** ✅
**URL:** https://www.promonitor.kz/dashboard/v2/

**Проверить:**
- [ ] Page loads without errors
- [ ] 6 metric cards displayed (Objects, Systems, Temperature, Alerts, Energy, Uptime)
- [ ] Live pulse animations on cards
- [ ] System status grid (12 items)
- [ ] Sidebar navigation visible
- [ ] Header controls (Theme/Mode switchers)
- [ ] Active page highlighting (Dashboard должен быть подсвечен)

**Expected Elements:**
```html
<div class="metrics-grid">
    <div class="metric-card">...</div> <!-- x6 -->
</div>
<div class="system-status-grid">
    <div class="status-item">...</div> <!-- x12 -->
</div>
```

**Check Console:** No JavaScript errors

---

### **3. Control Panel** ✅
**URL:** https://www.promonitor.kz/dashboard/v2/control/

**Проверить:**
- [ ] Page loads without errors
- [ ] 9 equipment nodes visible (colorful backgrounds)
- [ ] Hover effects working (scale + shadow)
- [ ] Animations running:
  - [ ] `sensor-scan` - rotating border (Sensor nodes)
  - [ ] `fan-spin` - icon rotation (Fan nodes)
  - [ ] `fire-flicker` - scale pulse (Boiler)
  - [ ] `flow` - particle animation (Pipelines)
- [ ] Click node → drawer opens on right
- [ ] Drawer shows device details
- [ ] Schema canvas background visible

**Expected Elements:**
```html
<div class="schema-canvas">
    <div class="equipment-node sensor">...</div> <!-- with sensor-scan -->
    <div class="equipment-node fan">...</div> <!-- with fan-spin -->
    <div class="equipment-node boiler">...</div> <!-- with fire-flicker -->
</div>
<div class="control-drawer">...</div>
```

**Check Animations:** Open DevTools → Elements → check if classes have animations

---

### **4. Analytics & Reports** ⭐ NEW
**URL:** https://www.promonitor.kz/dashboard/v2/analytics/

**Проверить:**
- [ ] Page loads without errors
- [ ] **Chart 1 (Temperature)** renders correctly:
  - [ ] Line chart with blue gradient
  - [ ] 7 data points visible
  - [ ] X-axis shows dates
  - [ ] Y-axis shows °C values
  - [ ] Date picker above chart (Flatpickr)
  - [ ] Export CSV button
- [ ] **Chart 2 (Pressure)** renders correctly:
  - [ ] Area chart with purple gradient
  - [ ] 24 data points (hourly)
  - [ ] Date picker functional
- [ ] **Chart 3 (Energy)** renders correctly:
  - [ ] Bar chart with green color
  - [ ] 30 bars (daily)
  - [ ] Date picker functional
- [ ] **5 Summary Cards** displayed:
  - [ ] Avg Temperature: 23.4°C
  - [ ] Avg Pressure: 2.85 bar
  - [ ] Total Energy: 4,350 kWh
  - [ ] Uptime: 99.8%
  - [ ] Efficiency Score: 94%
- [ ] Charts resize on window resize

**Expected Elements:**
```html
<div class="analytics-grid">
    <div class="chart-card">
        <canvas id="temperatureChart"></canvas>
    </div>
    <div class="chart-card">
        <canvas id="pressureChart"></canvas>
    </div>
    <div class="chart-card">
        <canvas id="energyChart"></canvas>
    </div>
</div>
<div class="summary-stats">
    <div class="stat-card">...</div> <!-- x5 -->
</div>
```

**Check Console:** Chart.js should load without errors

**Test Export CSV:**
1. Click "Export CSV" button on Temperature chart
2. Check browser Downloads folder
3. Open CSV file
4. Verify format:
   ```csv
   Date,Temperature (°C)
   2025-10-19,22.0
   2025-10-20,22.5
   ...
   ```

---

### **5. Alerts & Notifications** ⭐ NEW
**URL:** https://www.promonitor.kz/dashboard/v2/alerts/

**Проверить:**
- [ ] Page loads without errors
- [ ] **Alerts Table** displayed:
  - [ ] 8 mock alerts visible
  - [ ] Columns: Severity, Message, System, Time, Status, Actions
  - [ ] Severity badges colored correctly:
    - [ ] Critical (red)
    - [ ] Warning (orange)
    - [ ] Info (blue)
  - [ ] Status badges visible (Active/Acknowledged/Resolved)
- [ ] **Filter Buttons** working:
  - [ ] Click "All" → shows 8 alerts
  - [ ] Click "Critical" → shows 2 alerts
  - [ ] Click "Warning" → shows 3 alerts
  - [ ] Click "Info" → shows 3 alerts
  - [ ] Active filter highlighted
- [ ] **Summary Cards** displayed:
  - [ ] Total: 8
  - [ ] Active: 5
  - [ ] Acknowledged: 2
  - [ ] Resolved: 1
- [ ] **Time Updates:**
  - [ ] Wait 10 seconds
  - [ ] Times should update ("2 min ago" → "3 min ago")
- [ ] **Action Buttons:**
  - [ ] Acknowledge button visible for Active alerts
  - [ ] Resolve button visible for Acknowledged alerts
  - [ ] Click button → shows confirmation (mock)

**Expected Elements:**
```html
<div class="alerts-filters">
    <button class="filter-btn active">All (8)</button>
    <button class="filter-btn">Critical (2)</button>
    <button class="filter-btn">Warning (3)</button>
    <button class="filter-btn">Info (3)</button>
</div>
<div class="alerts-table-container">
    <table class="alerts-table">
        <tbody id="alertsTableBody">
            <tr class="alert-row warning">...</tr> <!-- x8 -->
        </tbody>
    </table>
</div>
```

**Check Console:** No errors, setInterval should run every 10s

---

### **6. Settings & Profile** ⭐ NEW
**URL:** https://www.promonitor.kz/dashboard/v2/settings/

**Проверить:**
- [ ] Page loads without errors
- [ ] **4 Settings Cards** displayed:

#### **Card 1: Profile (👤)**
- [ ] Avatar preview shows (initials or uploaded image)
- [ ] First Name field populated (if user has first_name)
- [ ] Last Name field populated
- [ ] Email field shows current user email
- [ ] Phone field visible
- [ ] "Upload Photo" button functional
- [ ] "Remove" button visible
- [ ] Save/Cancel buttons

#### **Card 2: Display (🎨)**
- [ ] Theme dropdown (Light/Dark/Auto)
- [ ] Mode dropdown (Monitoring/Control)
- [ ] Language dropdown (Русский/Қазақша/English)
- [ ] Timezone dropdown (Almaty/Nur-Sultan/Moscow/UTC)
- [ ] Apply/Reset buttons
- [ ] **Test Theme Switch:**
  1. Select "Dark"
  2. Click "Apply Settings"
  3. Page should switch to dark theme
  4. Reload page → theme persists (localStorage)

#### **Card 3: Notifications (🔔)**
- [ ] 5 checkboxes visible:
  - [ ] Email alerts (checked by default)
  - [ ] Weekly reports (checked)
  - [ ] SMS alerts (unchecked)
  - [ ] Browser notifications (checked)
  - [ ] Telegram bot (unchecked)
- [ ] Each checkbox has description text
- [ ] Save/Cancel buttons

#### **Card 4: Security (🔒)**
- [ ] Current password field
- [ ] New password field
- [ ] Confirm password field
- [ ] 2FA enable checkbox
- [ ] Change Password button
- [ ] **Danger Zone** visible:
  - [ ] Red border box
  - [ ] Warning text
  - [ ] "Delete Account" button (red)
- [ ] **Test Password Validation:**
  1. Enter new password < 8 chars
  2. Click "Change Password"
  3. Should show error: "Пароль должен быть минимум 8 символов!"
  4. Enter 8+ chars
  5. Enter different confirm password
  6. Should show: "Пароли не совпадают!"

**Expected Elements:**
```html
<div class="settings-grid">
    <div class="settings-card"> <!-- Profile -->
        <form id="profileForm">...</form>
    </div>
    <div class="settings-card"> <!-- Display -->
        <form id="displayForm">...</form>
    </div>
    <div class="settings-card"> <!-- Notifications -->
        <form id="notificationsForm">...</form>
    </div>
    <div class="settings-card"> <!-- Security -->
        <form id="securityForm">...</form>
    </div>
</div>
```

**Check Console:** Form submission handlers should work (mock save)

**Test Success Message:**
1. Fill any form
2. Click Save button
3. Green success message should appear at top
4. Message should auto-hide after 3 seconds

---

## 🎨 THEME & MODE TESTING

### **Theme Switcher (Header)**
1. Click Sun icon (🌙) in header
2. Page switches to Dark theme
3. All colors invert correctly
4. Click Moon icon (☀️)
5. Page switches back to Light theme
6. Reload page → theme persists

**Check localStorage:**
```javascript
localStorage.getItem('theme') // should be 'light' or 'dark'
```

### **Mode Switcher (Header)**
1. Click "Control" button in header
2. Mode switches to Control
3. Click "Monitoring" button
4. Mode switches back
5. Reload page → mode persists

**Check localStorage:**
```javascript
localStorage.getItem('mode') // should be 'monitoring' or 'control'
```

---

## 📱 RESPONSIVE TESTING

### **Desktop (1920px)**
- [ ] All cards visible
- [ ] Sidebar full width
- [ ] Charts render full size
- [ ] No horizontal scroll

### **Laptop (1366px)**
- [ ] Layout adjusts
- [ ] Sidebar still visible
- [ ] Cards stack properly

### **Tablet (768px)**
- [ ] Sidebar collapses to hamburger menu
- [ ] Cards stack vertically
- [ ] Touch interactions work

### **Mobile (375px)**
- [ ] Sidebar becomes overlay
- [ ] Single column layout
- [ ] Buttons full width
- [ ] Charts resize correctly

**Test Sidebar Toggle:**
1. Resize browser to 768px
2. Click hamburger menu (☰)
3. Sidebar slides in from left
4. Click outside → sidebar closes

---

## 🔍 BROWSER COMPATIBILITY

Test in multiple browsers:

- [ ] **Chrome** (Latest)
- [ ] **Firefox** (Latest)
- [ ] **Safari** (Latest)
- [ ] **Edge** (Latest)

**Check for:**
- CSS animations work
- Chart.js renders
- LocalStorage works
- No console errors

---

## 🚨 ERROR HANDLING

### **Expected Errors (None):**
- [ ] No 500 Internal Server Error
- [ ] No 404 Not Found
- [ ] No JavaScript errors in console
- [ ] No broken images
- [ ] No CSS loading issues

### **If Errors Occur:**
1. Check Railway deployment logs
2. Verify commit `ca25cc6` deployed successfully
3. Check browser console for details
4. Report issue with screenshot

---

## ✅ FINAL CHECKLIST

### **All Pages Accessible:**
- [ ] Dashboard (/)
- [ ] Control (/control/)
- [ ] Analytics (/analytics/) ⭐
- [ ] Alerts (/alerts/) ⭐
- [ ] Settings (/settings/) ⭐

### **All Features Working:**
- [ ] Navigation (sidebar + submenu)
- [ ] Animations (6 types)
- [ ] Theme switcher (Dark/Light)
- [ ] Mode switcher (Monitoring/Control)
- [ ] Charts rendering (Chart.js)
- [ ] Date pickers (Flatpickr)
- [ ] Alert filtering
- [ ] Forms submission (mock)
- [ ] Success messages

### **All Data Visible:**
- [ ] Dashboard metrics (6 cards)
- [ ] Control nodes (9 devices)
- [ ] Analytics charts (3 graphs)
- [ ] Alerts table (8 alerts)
- [ ] Settings forms (4 cards)

---

## 📊 TEST RESULTS TEMPLATE

```
=== PHASE 2 TESTING RESULTS ===

Tested By: [Your Name]
Date: [Date]
Commit: ca25cc6
Environment: Production (www.promonitor.kz)

PAGES TESTED:
✅ Dashboard - All features working
✅ Control Panel - Animations OK, Drawer functional
✅ Analytics - Charts rendering, Export CSV OK
✅ Alerts - Filtering working, Times updating
✅ Settings - All forms functional, Theme switch OK

ISSUES FOUND:
- [None / List any issues]

BROWSER TESTED:
- Chrome 120.0 ✅
- Firefox 121.0 ✅
- Safari 17.2 ✅

RESPONSIVE TESTED:
- Desktop (1920px) ✅
- Laptop (1366px) ✅
- Tablet (768px) ✅
- Mobile (375px) ✅

OVERALL STATUS: ✅ PASSED / ❌ FAILED

NOTES:
[Any additional observations]
```

---

## 🎯 SUCCESS CRITERIA

Phase 2 считается успешно завершенной если:

1. ✅ Все 5 страниц загружаются без ошибок
2. ✅ Все анимации работают плавно
3. ✅ Theme/Mode switchers функциональны с localStorage
4. ✅ Chart.js графики отображаются корректно
5. ✅ Alert filtering работает
6. ✅ Forms показывают success messages
7. ✅ Responsive design работает на всех размерах
8. ✅ Нет JavaScript ошибок в console
9. ✅ Нет 404/500 ошибок
10. ✅ 100% соответствие утверждённому макету

---

**Generated:** 2025-10-25  
**Version:** Phase 2 Testing Guide  
**Status:** Ready for QA
