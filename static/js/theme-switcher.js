/**
 * ProMonitor Theme Switcher
 * Переключение между светлой и тёмной темой
 */

// Инициализация темы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем сохранённую тему
    const savedTheme = localStorage.getItem('promonitor-theme') || 'light';
    setTheme(savedTheme);
    
    // Обработчик кнопки переключения
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

/**
 * Установка темы
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('promonitor-theme', theme);
    
    // Обновляем иконку кнопки
    updateThemeIcon(theme);
}

/**
 * Переключение темы
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Плавная анимация перехода
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    setTheme(newTheme);
}

/**
 * Обновление иконки переключателя
 */
function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle .icon');
    if (!icon) return;
    
    if (theme === 'dark') {
        icon.innerHTML = '🌙';
        icon.setAttribute('title', 'Переключить на светлую тему');
    } else {
        icon.innerHTML = '☀️';
        icon.setAttribute('title', 'Переключить на тёмную тему');
    }
}

/**
 * Получение текущей темы
 */
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

/**
 * Экспорт для использования в других скриптах
 */
window.ProMonitorTheme = {
    setTheme: setTheme,
    toggleTheme: toggleTheme,
    getCurrentTheme: getCurrentTheme
};
