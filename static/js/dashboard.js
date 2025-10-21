/**
 * ProMonitor Dashboard JavaScript
 * Графики Chart.js и анимации gauge индикаторов
 */

// Цвета из логотипа ProMonitor
const BRAND_COLORS = {
    blue: '#0078D4',
    orange: '#FF8C42',
    darkBlue: '#005A9E',
    lightOrange: '#FF9E5C'
};

/**
 * Создание графика энергопотребления
 */
function createPowerChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Определяем цвета в зависимости от темы
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const textColor = theme === 'dark' ? '#E8EDF5' : '#1E2A38';
    const gridColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Энергопотребление (кВт)',
                data: data.values,
                borderColor: BRAND_COLORS.blue,
                backgroundColor: 'rgba(0, 120, 212, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: BRAND_COLORS.blue,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: textColor,
                        font: {
                            size: 14,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: theme === 'dark' ? '#142642' : '#FFFFFF',
                    titleColor: textColor,
                    bodyColor: textColor,
                    borderColor: BRAND_COLORS.blue,
                    borderWidth: 2,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + ' кВт';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return value + ' кВт';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Обновление gauge индикатора
 */
function updateGauge(selector, value, min, max) {
    const gauge = document.querySelector(selector);
    if (!gauge) return;
    
    // Вычисляем процент для анимации
    const percentage = ((value - min) / (max - min)) * 100;
    const circumference = 251.2; // Длина дуги gauge
    const offset = circumference - (circumference * percentage / 100);
    
    // Анимация stroke-dashoffset
    gauge.style.transition = 'stroke-dashoffset 1s ease';
    gauge.style.strokeDashoffset = offset;
}

/**
 * Анимация всех gauge при загрузке
 */
function animateGauges() {
    // Температура (пример: 23°C из диапазона 0-50°C)
    const tempElement = document.querySelector('.temp-gauge');
    if (tempElement) {
        const tempValue = parseFloat(tempElement.getAttribute('data-value') || 23);
        updateGauge('.temp-gauge', tempValue, 0, 50);
    }
    
    // Влажность (пример: 55% из диапазона 0-100%)
    const humElement = document.querySelector('.hum-gauge');
    if (humElement) {
        const humValue = parseFloat(humElement.getAttribute('data-value') || 55);
        updateGauge('.hum-gauge', humValue, 0, 100);
    }
    
    // Мощность (пример: 145 кВт из диапазона 0-300 кВт)
    const powElement = document.querySelector('.pow-gauge');
    if (powElement) {
        const powValue = parseFloat(powElement.getAttribute('data-value') || 145);
        updateGauge('.pow-gauge', powValue, 0, 300);
    }
}

/**
 * Генерация тестовых данных для графика
 */
function generateMockData() {
    const labels = [];
    const values = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        labels.push(time.getHours() + ':00');
        
        // Генерируем реалистичные значения с небольшими колебаниями
        const baseValue = 120;
        const variation = Math.sin(i / 3) * 30 + Math.random() * 20;
        values.push(Math.round(baseValue + variation));
    }
    
    return { labels, values };
}

/**
 * Инициализация дашборда
 */
document.addEventListener('DOMContentLoaded', function() {
    // Анимация gauge индикаторов
    setTimeout(animateGauges, 100);
    
    // Создание графика энергопотребления
    const chartCanvas = document.getElementById('powerChart');
    if (chartCanvas) {
        const mockData = generateMockData();
        createPowerChart('powerChart', mockData);
    }
    
    // Обновление графика при смене темы
    document.getElementById('themeToggle')?.addEventListener('click', function() {
        setTimeout(() => {
            const chartCanvas = document.getElementById('powerChart');
            if (chartCanvas && Chart.getChart(chartCanvas)) {
                const chart = Chart.getChart(chartCanvas);
                chart.destroy();
                
                const mockData = generateMockData();
                createPowerChart('powerChart', mockData);
            }
        }, 300); // Задержка для завершения анимации смены темы
    });
    
    // Автообновление данных каждые 30 секунд
    setInterval(function() {
        // Здесь будет реальный запрос к API
        fetch('/dashboard-data/')
            .then(response => response.json())
            .then(data => {
                // Обновление gauge индикаторов
                if (data.temperature) updateGauge('.temp-gauge', data.temperature, 0, 50);
                if (data.humidity) updateGauge('.hum-gauge', data.humidity, 0, 100);
                if (data.power) updateGauge('.pow-gauge', data.power, 0, 300);
                
                // Обновление значений
                document.querySelectorAll('.gauge-value').forEach((el, index) => {
                    if (index === 0 && data.temperature) el.textContent = data.temperature + '°C';
                    if (index === 1 && data.humidity) el.textContent = data.humidity + '%';
                    if (index === 2 && data.power) el.textContent = data.power + ' кВт';
                });
            })
            .catch(err => console.log('Автообновление будет доступно после интеграции API'));
    }, 30000);
});

/**
 * Экспорт функций для использования в других скриптах
 */
window.ProMonitorDashboard = {
    createPowerChart: createPowerChart,
    updateGauge: updateGauge,
    animateGauges: animateGauges
};
