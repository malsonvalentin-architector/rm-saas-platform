/**
 * ProMonitor - Live Charts для страницы Actuators
 * Phase 4.5 - Real-Time Features
 */

// Глобальные переменные для хранения chart instances
let commandsTimelineChart = null;
let activityChart = null;
let devicesPieChart = null;

// Интервал обновления (10 секунд)
const REFRESH_INTERVAL = 10000;

/**
 * Инициализация всех live charts
 */
function initLiveCharts() {
    console.log('🎨 Инициализация Live Charts...');
    
    // Инициализируем каждый график
    initCommandsTimelineChart();
    initActivityChart();
    initDevicesPieChart();
    
    // Запускаем автообновление статистики
    updateLiveStats();
    setInterval(updateLiveStats, REFRESH_INTERVAL);
    
    // Индикатор "Live"
    startLiveIndicator();
    
    console.log('✅ Live Charts инициализированы');
}

/**
 * График команд за 24 часа (Timeline)
 */
function initCommandsTimelineChart() {
    const ctx = document.getElementById('commandsTimelineChart');
    if (!ctx) {
        console.warn('⚠️ Canvas commandsTimelineChart не найден');
        return;
    }
    
    commandsTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Команды',
                data: [],
                borderColor: '#0078D4',
                backgroundColor: 'rgba(0, 120, 212, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '📊 Команды за последние 24 часа',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    // Загружаем начальные данные
    updateCommandsTimelineChart();
    
    // Автообновление каждые 10 секунд
    setInterval(updateCommandsTimelineChart, REFRESH_INTERVAL);
}

/**
 * Обновление данных графика команд
 */
async function updateCommandsTimelineChart() {
    try {
        const response = await fetch('/api/actuators/commands-timeline/');
        const data = await response.json();
        
        if (commandsTimelineChart) {
            commandsTimelineChart.data.labels = data.labels;
            commandsTimelineChart.data.datasets[0].data = data.data;
            commandsTimelineChart.update();
            
            console.log('📈 Commands Timeline обновлён:', data.data.length, 'точек');
        }
    } catch (error) {
        console.error('❌ Ошибка обновления Commands Timeline:', error);
    }
}

/**
 * График активности за последний час (5-минутные интервалы)
 */
function initActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) {
        console.warn('⚠️ Canvas activityChart не найден');
        return;
    }
    
    activityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Активность',
                data: [],
                backgroundColor: '#FF8C42',
                borderColor: '#D9711A',
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '⚡ Активность за последний час',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    // Загружаем начальные данные
    updateActivityChart();
    
    // Автообновление каждые 10 секунд
    setInterval(updateActivityChart, REFRESH_INTERVAL);
}

/**
 * Обновление данных графика активности
 */
async function updateActivityChart() {
    try {
        const response = await fetch('/api/actuators/activity-chart/');
        const data = await response.json();
        
        if (activityChart) {
            activityChart.data.labels = data.labels;
            activityChart.data.datasets[0].data = data.data;
            activityChart.update();
            
            console.log('📊 Activity Chart обновлён:', data.data.length, 'точек');
        }
    } catch (error) {
        console.error('❌ Ошибка обновления Activity Chart:', error);
    }
}

/**
 * Pie Chart - устройства по типам
 */
function initDevicesPieChart() {
    const ctx = document.getElementById('devicesPieChart');
    if (!ctx) {
        console.warn('⚠️ Canvas devicesPieChart не найден');
        return;
    }
    
    devicesPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#0078D4',
                    '#FF8C42',
                    '#2ECC71',
                    '#E74C3C',
                    '#9B59B6',
                    '#F39C12',
                    '#1ABC9C',
                    '#E67E22',
                    '#3498DB'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 10
                    }
                },
                title: {
                    display: true,
                    text: '🎯 Устройства по типам',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 750
            }
        }
    });
    
    // Загружаем начальные данные
    updateDevicesPieChart();
    
    // Автообновление каждые 30 секунд (это медленнее меняется)
    setInterval(updateDevicesPieChart, 30000);
}

/**
 * Обновление Pie Chart
 */
async function updateDevicesPieChart() {
    try {
        const response = await fetch('/api/actuators/by-type/');
        const data = await response.json();
        
        if (devicesPieChart) {
            devicesPieChart.data.labels = data.labels;
            devicesPieChart.data.datasets[0].data = data.data;
            devicesPieChart.update();
            
            console.log('🥧 Pie Chart обновлён:', data.labels.length, 'типов');
        }
    } catch (error) {
        console.error('❌ Ошибка обновления Pie Chart:', error);
    }
}

/**
 * Обновление live статистики на карточках
 */
async function updateLiveStats() {
    try {
        const response = await fetch('/api/actuators/live-stats/');
        const data = await response.json();
        
        // Обновляем карточки статистики
        updateStatCard('total-devices', data.stats.total);
        updateStatCard('online-devices', data.stats.online);
        updateStatCard('active-devices', data.stats.active);
        updateStatCard('commands-24h', data.stats.commands_24h);
        
        // Обновляем список последних команд
        updateRecentCommands(data.recent_commands);
        
        console.log('📊 Live Stats обновлена');
    } catch (error) {
        console.error('❌ Ошибка обновления Live Stats:', error);
    }
}

/**
 * Обновление значения в статистической карточке с анимацией
 */
function updateStatCard(cardId, newValue) {
    const element = document.getElementById(cardId);
    if (!element) return;
    
    const currentValue = parseInt(element.textContent) || 0;
    
    if (currentValue !== newValue) {
        // Анимация изменения
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
        }, 150);
    }
}

/**
 * Обновление списка последних команд
 */
function updateRecentCommands(commands) {
    const container = document.getElementById('recent-commands-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    commands.forEach(cmd => {
        const statusIcon = cmd.success ? '✅' : '❌';
        const timeAgo = getTimeAgo(new Date(cmd.timestamp));
        
        const item = document.createElement('div');
        item.className = 'list-group-item';
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${cmd.actuator_name}</strong>
                    <br>
                    <small class="text-muted">${cmd.object_name}</small>
                </div>
                <div class="text-end">
                    <span class="badge bg-primary">${cmd.value}</span>
                    <span>${statusIcon}</span>
                    <br>
                    <small class="text-muted">${timeAgo}</small>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

/**
 * Форматирование времени "X минут назад"
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds} сек назад`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} мин назад`;
    const hours = Math.floor(minutes / 60);
    return `${hours} ч назад`;
}

/**
 * Индикатор "Live" с мигающей точкой
 */
function startLiveIndicator() {
    const indicator = document.getElementById('live-indicator');
    if (!indicator) return;
    
    setInterval(() => {
        indicator.classList.toggle('pulse');
    }, 1000);
}

// Инициализация при загрузке страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLiveCharts);
} else {
    initLiveCharts();
}
