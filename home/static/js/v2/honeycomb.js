/**
 * ProMonitor V2 - Honeycomb Building Map
 * Interactive SVG-based hexagonal building visualization
 * Inspired by Zabbix network topology maps
 */

class HoneycombMap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            hexSize: 40,
            spacing: 8,
            columns: 6,
            rows: 4,
            ...options
        };
        
        this.buildings = [];
        this.svg = null;
        this.selectedBuilding = null;
        
        this.init();
    }
    
    init() {
        this.createSVG();
        this.setupEventListeners();
    }
    
    createSVG() {
        const width = (this.options.columns * this.options.hexSize * 1.75) + 100;
        const height = (this.options.rows * this.options.hexSize * 1.5) + 100;
        
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', width);
        this.svg.setAttribute('height', height);
        this.svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        this.svg.classList.add('honeycomb-map');
        
        // Create gradient definitions
        this.createGradients();
        
        this.container.appendChild(this.svg);
    }
    
    createGradients() {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        
        // Status gradients
        const statuses = ['healthy', 'warning', 'critical', 'offline'];
        const colors = {
            healthy: ['#4ade80', '#22c55e'],
            warning: ['#fbbf24', '#f59e0b'],
            critical: ['#ef4444', '#dc2626'],
            offline: ['#6b7280', '#4b5563']
        };
        
        statuses.forEach(status => {
            const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            gradient.setAttribute('id', `gradient-${status}`);
            gradient.setAttribute('x1', '0%');
            gradient.setAttribute('y1', '0%');
            gradient.setAttribute('x2', '100%');
            gradient.setAttribute('y2', '100%');
            
            const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop1.setAttribute('offset', '0%');
            stop1.setAttribute('stop-color', colors[status][0]);
            
            const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop2.setAttribute('offset', '100%');
            stop2.setAttribute('stop-color', colors[status][1]);
            
            gradient.appendChild(stop1);
            gradient.appendChild(stop2);
            defs.appendChild(gradient);
        });
        
        // Glow filter
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.setAttribute('id', 'glow');
        filter.setAttribute('x', '-50%');
        filter.setAttribute('y', '-50%');
        filter.setAttribute('width', '200%');
        filter.setAttribute('height', '200%');
        
        const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
        feGaussianBlur.setAttribute('stdDeviation', '3');
        feGaussianBlur.setAttribute('result', 'coloredBlur');
        
        const feMerge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge');
        const feMergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode1.setAttribute('in', 'coloredBlur');
        const feMergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode2.setAttribute('in', 'SourceGraphic');
        
        feMerge.appendChild(feMergeNode1);
        feMerge.appendChild(feMergeNode2);
        filter.appendChild(feGaussianBlur);
        filter.appendChild(feMerge);
        
        defs.appendChild(filter);
        this.svg.appendChild(defs);
    }
    
    generateHexagonPath(x, y, size) {
        const points = [];
        for (let i = 0; i < 6; i++) {
            const angle = (Math.PI / 3) * i;
            const px = x + size * Math.cos(angle);
            const py = y + size * Math.sin(angle);
            points.push(`${px},${py}`);
        }
        return `M ${points.join(' L ')} Z`;
    }
    
    calculateHexPosition(col, row) {
        const hexWidth = this.options.hexSize * 1.75;
        const hexHeight = this.options.hexSize * 1.5;
        
        const x = 50 + col * hexWidth + (row % 2) * (hexWidth / 2);
        const y = 50 + row * hexHeight;
        
        return { x, y };
    }
    
    addBuilding(building) {
        const position = this.buildings.length;
        const col = position % this.options.columns;
        const row = Math.floor(position / this.options.columns);
        
        if (row >= this.options.rows) {
            console.warn('Building exceeds map capacity');
            return;
        }
        
        const { x, y } = this.calculateHexPosition(col, row);
        
        building.position = { x, y, col, row };
        building.id = building.id || `building-${position}`;
        
        this.buildings.push(building);
        this.renderBuilding(building);
    }
    
    renderBuilding(building) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'building-hex');
        group.setAttribute('data-building-id', building.id);
        group.setAttribute('transform', `translate(${building.position.x}, ${building.position.y})`);
        
        // Main hexagon
        const hex = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        hex.setAttribute('d', this.generateHexagonPath(0, 0, this.options.hexSize));
        hex.setAttribute('fill', `url(#gradient-${building.status})`);
        hex.setAttribute('stroke', '#333');
        hex.setAttribute('stroke-width', '2');
        hex.setAttribute('class', `hex-${building.status}`);
        
        // Inner decoration ring
        const innerHex = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        innerHex.setAttribute('d', this.generateHexagonPath(0, 0, this.options.hexSize * 0.8));
        innerHex.setAttribute('fill', 'none');
        innerHex.setAttribute('stroke', 'rgba(255,255,255,0.3)');
        innerHex.setAttribute('stroke-width', '1');
        
        // Building icon
        const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        icon.setAttribute('x', '0');
        icon.setAttribute('y', '5');
        icon.setAttribute('text-anchor', 'middle');
        icon.setAttribute('font-family', 'Material Icons');
        icon.setAttribute('font-size', '24');
        icon.setAttribute('fill', 'white');
        icon.textContent = building.icon || '🏢';
        
        // Building name
        const name = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        name.setAttribute('x', '0');
        name.setAttribute('y', this.options.hexSize + 20);
        name.setAttribute('text-anchor', 'middle');
        name.setAttribute('font-family', 'Inter, sans-serif');
        name.setAttribute('font-size', '12');
        name.setAttribute('font-weight', '500');
        name.setAttribute('fill', 'var(--text-primary)');
        name.textContent = building.name;
        
        // Status indicator
        const statusDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        statusDot.setAttribute('cx', this.options.hexSize * 0.6);
        statusDot.setAttribute('cy', -this.options.hexSize * 0.6);
        statusDot.setAttribute('r', '6');
        statusDot.setAttribute('fill', this.getStatusColor(building.status));
        statusDot.setAttribute('stroke', '#000');
        statusDot.setAttribute('stroke-width', '1');
        
        // Sensor count badge
        if (building.sensorCount) {
            const badge = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            badge.setAttribute('cx', -this.options.hexSize * 0.6);
            badge.setAttribute('cy', -this.options.hexSize * 0.6);
            badge.setAttribute('r', '10');
            badge.setAttribute('fill', '#1e40af');
            badge.setAttribute('stroke', '#fff');
            badge.setAttribute('stroke-width', '2');
            
            const badgeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            badgeText.setAttribute('x', -this.options.hexSize * 0.6);
            badgeText.setAttribute('y', -this.options.hexSize * 0.6 + 4);
            badgeText.setAttribute('text-anchor', 'middle');
            badgeText.setAttribute('font-family', 'Inter, sans-serif');
            badgeText.setAttribute('font-size', '10');
            badgeText.setAttribute('font-weight', 'bold');
            badgeText.setAttribute('fill', 'white');
            badgeText.textContent = building.sensorCount;
            
            group.appendChild(badge);
            group.appendChild(badgeText);
        }
        
        group.appendChild(hex);
        group.appendChild(innerHex);
        group.appendChild(icon);
        group.appendChild(name);
        group.appendChild(statusDot);
        
        // Add hover effects
        group.addEventListener('mouseenter', () => this.onBuildingHover(building, group));
        group.addEventListener('mouseleave', () => this.onBuildingLeave(building, group));
        group.addEventListener('click', () => this.onBuildingClick(building, group));
        
        this.svg.appendChild(group);
    }
    
    getStatusColor(status) {
        const colors = {
            healthy: '#22c55e',
            warning: '#f59e0b',
            critical: '#dc2626',
            offline: '#6b7280'
        };
        return colors[status] || colors.offline;
    }
    
    onBuildingHover(building, element) {
        element.style.filter = 'url(#glow)';
        element.style.transform = 'scale(1.1)';
        element.style.transformOrigin = 'center';
        element.style.transition = 'all 0.2s ease';
        
        this.showTooltip(building, element);
    }
    
    onBuildingLeave(building, element) {
        element.style.filter = 'none';
        element.style.transform = 'scale(1)';
        
        this.hideTooltip();
    }
    
    onBuildingClick(building, element) {
        if (this.selectedBuilding) {
            this.selectedBuilding.element.classList.remove('selected');
        }
        
        this.selectedBuilding = { building, element };
        element.classList.add('selected');
        
        this.showBuildingDetails(building);
        
        // Emit custom event
        const event = new CustomEvent('buildingSelected', {
            detail: { building }
        });
        this.container.dispatchEvent(event);
    }
    
    showTooltip(building, element) {
        const tooltip = document.createElement('div');
        tooltip.className = 'honeycomb-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-header">
                <strong>${building.name}</strong>
                <span class="status-badge status-${building.status}">${building.status}</span>
            </div>
            <div class="tooltip-body">
                <div class="tooltip-stat">
                    <span class="label">Датчики:</span>
                    <span class="value">${building.sensorCount || 0}</span>
                </div>
                <div class="tooltip-stat">
                    <span class="label">Температура:</span>
                    <span class="value">${building.temperature || 'N/A'}°C</span>
                </div>
                <div class="tooltip-stat">
                    <span class="label">Влажность:</span>
                    <span class="value">${building.humidity || 'N/A'}%</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 10}px`;
        tooltip.style.transform = 'translate(-50%, -100%)';
        
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    showBuildingDetails(building) {
        const sidebar = document.querySelector('.building-details-sidebar');
        if (sidebar) {
            sidebar.innerHTML = `
                <div class="building-details-header">
                    <h3>${building.name}</h3>
                    <div class="status-indicator status-${building.status}">
                        <span class="status-dot"></span>
                        ${building.status}
                    </div>
                </div>
                
                <div class="building-stats">
                    <div class="stat-card">
                        <div class="stat-value">${building.sensorCount || 0}</div>
                        <div class="stat-label">Активных датчиков</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${building.temperature || '--'}°C</div>
                        <div class="stat-label">Средняя температура</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${building.humidity || '--'}%</div>
                        <div class="stat-label">Средняя влажность</div>
                    </div>
                </div>
                
                <div class="sensor-list">
                    <h4>Датчики в здании</h4>
                    <div class="sensors">
                        ${building.sensors ? building.sensors.map(sensor => `
                            <div class="sensor-item status-${sensor.status}">
                                <div class="sensor-name">${sensor.name}</div>
                                <div class="sensor-value">${sensor.value} ${sensor.unit}</div>
                            </div>
                        `).join('') : '<div class="no-sensors">Нет данных о датчиках</div>'}
                    </div>
                </div>
                
                <div class="building-actions">
                    <button class="btn btn-primary" onclick="viewBuildingDetail('${building.id}')">
                        Подробнее
                    </button>
                    <button class="btn btn-secondary" onclick="configureSensors('${building.id}')">
                        Настройки
                    </button>
                </div>
            `;
            sidebar.classList.add('active');
        }
    }
    
    updateBuilding(buildingId, updates) {
        const building = this.buildings.find(b => b.id === buildingId);
        if (!building) return;
        
        Object.assign(building, updates);
        
        // Re-render the building
        const element = this.svg.querySelector(`[data-building-id="${buildingId}"]`);
        if (element) {
            element.remove();
            this.renderBuilding(building);
        }
    }
    
    setFilter(status) {
        this.svg.querySelectorAll('.building-hex').forEach(element => {
            const buildingId = element.getAttribute('data-building-id');
            const building = this.buildings.find(b => b.id === buildingId);
            
            if (status === 'all' || building.status === status) {
                element.style.opacity = '1';
                element.style.pointerEvents = 'all';
            } else {
                element.style.opacity = '0.3';
                element.style.pointerEvents = 'none';
            }
        });
    }
    
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.selectedBuilding) {
                this.selectedBuilding.element.classList.remove('selected');
                this.selectedBuilding = null;
                
                const sidebar = document.querySelector('.building-details-sidebar');
                if (sidebar) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
    
    // Public API methods
    loadBuildings(buildings) {
        this.clearMap();
        buildings.forEach(building => this.addBuilding(building));
    }
    
    clearMap() {
        this.buildings = [];
        this.svg.querySelectorAll('.building-hex').forEach(el => el.remove());
    }
    
    getSelectedBuilding() {
        return this.selectedBuilding ? this.selectedBuilding.building : null;
    }
    
    selectBuilding(buildingId) {
        const building = this.buildings.find(b => b.id === buildingId);
        const element = this.svg.querySelector(`[data-building-id="${buildingId}"]`);
        
        if (building && element) {
            this.onBuildingClick(building, element);
        }
    }
    
    resize() {
        // Recalculate SVG dimensions if container size changed
        const containerRect = this.container.getBoundingClientRect();
        const aspectRatio = this.svg.getAttribute('viewBox').split(' ');
        const width = aspectRatio[2];
        const height = aspectRatio[3];
        
        if (containerRect.width < parseInt(width)) {
            this.svg.style.width = '100%';
            this.svg.style.height = 'auto';
        }
    }
}

// Export for use in other modules
window.HoneycombMap = HoneycombMap;

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if honeycomb container exists
    const container = document.getElementById('honeycomb-container');
    if (container) {
        window.buildingMap = new HoneycombMap('honeycomb-container', {
            hexSize: 45,
            spacing: 10,
            columns: 5,
            rows: 3
        });
        
        // Load demo data if in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            loadDemoBuildings();
        }
    }
});

// Demo data for development
function loadDemoBuildings() {
    const demoBuildings = [
        {
            id: 'building-1',
            name: 'Офис А',
            status: 'healthy',
            sensorCount: 12,
            temperature: 22.5,
            humidity: 45,
            icon: '🏢',
            sensors: [
                { name: 'Температура Зал 1', value: '22.5', unit: '°C', status: 'healthy' },
                { name: 'Влажность Зал 1', value: '45', unit: '%', status: 'healthy' },
                { name: 'CO2 Зал 1', value: '420', unit: 'ppm', status: 'warning' }
            ]
        },
        {
            id: 'building-2',
            name: 'Склад Б',
            status: 'warning',
            sensorCount: 8,
            temperature: 18.2,
            humidity: 65,
            icon: '🏭',
            sensors: [
                { name: 'Температура Склад', value: '18.2', unit: '°C', status: 'healthy' },
                { name: 'Влажность Склад', value: '65', unit: '%', status: 'warning' }
            ]
        },
        {
            id: 'building-3',
            name: 'ЦОД',
            status: 'critical',
            sensorCount: 24,
            temperature: 28.9,
            humidity: 35,
            icon: '💻',
            sensors: [
                { name: 'Температура Сервер 1', value: '28.9', unit: '°C', status: 'critical' },
                { name: 'Влажность ЦОД', value: '35', unit: '%', status: 'healthy' }
            ]
        },
        {
            id: 'building-4',
            name: 'Лабория',
            status: 'healthy',
            sensorCount: 16,
            temperature: 21.0,
            humidity: 50,
            icon: '🔬'
        },
        {
            id: 'building-5',
            name: 'Архив',
            status: 'offline',
            sensorCount: 0,
            temperature: null,
            humidity: null,
            icon: '📚'
        }
    ];
    
    if (window.buildingMap) {
        window.buildingMap.loadBuildings(demoBuildings);
    }
}

// Global helper functions for button actions
window.viewBuildingDetail = function(buildingId) {
    window.location.href = `/buildings/${buildingId}/`;
};

window.configureSensors = function(buildingId) {
    window.location.href = `/buildings/${buildingId}/sensors/`;
};