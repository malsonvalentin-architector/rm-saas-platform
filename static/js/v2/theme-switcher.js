// ProMonitor v2 - Theme Switcher

class ThemeSwitcher {
    constructor() {
        this.currentTheme = this.loadTheme();
        this.init();
    }

    init() {
        // Apply saved theme
        this.applyTheme(this.currentTheme);
        
        // Setup event listeners
        this.setupListeners();
    }

    loadTheme() {
        // Check localStorage
        const saved = localStorage.getItem('promonitor-theme');
        if (saved) return saved;
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        
        return 'dark'; // Default
    }

    saveTheme(theme) {
        localStorage.setItem('promonitor-theme', theme);
        
        // Save to backend (AJAX)
        if (typeof $ !== 'undefined') {
            $.ajax({
                url: '/api/user/preferences/',
                method: 'POST',
                data: {
                    theme: theme,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    console.log('Theme preference saved');
                }
            });
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.updateButtons(theme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        this.saveTheme(newTheme);
    }

    updateButtons(theme) {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            if (btn.dataset.theme === theme) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    setupListeners() {
        // Theme button clicks
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const theme = btn.dataset.theme;
                this.applyTheme(theme);
                this.saveTheme(theme);
            });
        });

        // Listen to system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (!localStorage.getItem('promonitor-theme')) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeSwitcher;
}
