/**
 * ProMonitor V2 - Honeycomb Building Map
 * Interactive hexagonal building layout with SVG visualization
 */

class HoneycombMap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.options = {
            hexSize: 60,
            gap: 10,
            cols: 6,
            rows: 4,
            ...options
        };

        this.buildings = [];
        this.selectedBuilding = null;
        this.tooltip = null;
        this.svg = null;

        this.init();
    }

    init() {
        this.createLayout();
        this.createTooltip();
        this.loadDemoData();
        this.render();
    }

    createLayout() {
        this.container.innerHTML = `
            <div class="honeycomb-container">
                <div class="honeycomb-map">
                    <svg class="honeycomb-svg" id="honeycomb-svg"></svg>
                    <div class="zoom-controls">
                        <button class="zoom-btn" id="zoom-in" title="Zoom In">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button class="zoom-btn" id="zoom-out" title="Zoom Out">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button class="zoom-btn" id="zoom-reset" title="Reset Zoom">
                            <i class="fas fa-expand"></i>
                        </button>
                    </div>
                </div>
                <div class="honeycomb-sidebar">
                    <div class="sidebar-header">
                        <div class="sidebar-title">Building Overview</div>
                        <div class="sidebar-subtitle">Click on a building to view details</div>
                    </div>
                    <div class="honeycomb-legend">
                        <div class="legend-item">
                            <div class="legend-color online"></div>
                            <span class="legend-label">Online</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color warning"></div>
                            <span class="legend-label">Warning</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color critical"></div>
                            <span class="legend-label">Critical</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color offline"></div>
                            <span class="legend-label">Offline</span>
                        </div>
                    </div>
                    <div id="building-details"></div>
                </div>
            </div>
        `;

        this.svg = document.getElementById('honeycomb-svg');
        this.setupZoomControls();
    }

    setupZoomControls() {
        // Zoom controls implementation
        let scale = 1;
        const zoomIn = () => {
            scale = Math.min(scale + 0.2, 2);
            this.svg.style.transform = `scale(${scale})`;
        };
        const zoomOut = () => {
            scale = Math.max(scale - 0.2, 0.5);
            this.svg.style.transform = `scale(${scale})`;
        };
        const zoomReset = () => {
            scale = 1;
            this.svg.style.transform = 'scale(1)';
        };

        document.getElementById('zoom-in')?.addEventListener('click', zoomIn);
        document.getElementById('zoom-out')?.addEventListener('click', zoomOut);
        document.getElementById('zoom-reset')?.addEventListener('click', zoomReset);
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'hexagon-tooltip';
        this.container.querySelector('.honeycomb-map').appendChild(this.tooltip);
    }

    loadDemoData() {
        // Demo buildings data
        const statuses = ['online', 'warning', 'critical', 'offline'];
        const types = ['office', 'warehouse', 'datacenter', 'factory'];
        const icons = {
            office: '🏢',
            warehouse: '📦',
            datacenter: '💻',
            factory: '🏭'
        };

        for (let i = 0; i < this.options.cols * this.options.rows; i++) {
            const type = types[Math.floor(Math.random() * types.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            
            this.buildings.push({
                id: `building-${i + 1}`,
                name: `Building ${i + 1}`,
                type: type,
                icon: icons[type],
                status: status,
                sensors: Math.floor(Math.random() * 50) + 10,
                activeSensors: Math.floor(Math.random() * 40) + 5,
                alerts: status === 'critical' ? Math.floor(Math.random() * 5) + 1 : 
                        status === 'warning' ? Math.floor(Math.random() * 3) : 0,
                temperature: (Math.random() * 10 + 18).toFixed(1),
                humidity: (Math.random() * 30 + 40).toFixed(0),
                lastUpdate: this.getRandomTime()
            });
        }
    }

    getRandomTime() {
        const minutes = Math.floor(Math.random() * 60);
        return `${minutes} min ago`;
    }

    render() {
        this.renderHexagons();
        this.renderEmptyState();
    }

    renderHexagons() {
        const { hexSize, gap, cols } = this.options;
        const hexWidth = hexSize * 2;
        const hexHeight = Math.sqrt(3) * hexSize;
        const horizontalSpacing = hexWidth * 0.75 + gap;
        const verticalSpacing = hexHeight + gap;

        const svgWidth = cols * horizontalSpacing + hexWidth * 0.25;
        const svgHeight = this.buildings.length / cols * verticalSpacing + hexHeight;

        this.svg.setAttribute('viewBox', `0 0 ${svgWidth} ${svgHeight}`);
        this.svg.innerHTML = '';

        this.buildings.forEach((building, index) => {
            const col = index % cols;
            const row = Math.floor(index / cols);
            const x = col * horizontalSpacing + hexSize;
            const y = row * verticalSpacing + hexSize + (col % 2 === 1 ? verticalSpacing / 2 : 0);

            this.createHexagon(building, x, y, hexSize);
        });
    }

    createHexagon(building, cx, cy, size) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.classList.add('hexagon-cell', `status-${building.status}`);
        group.setAttribute('data-building-id', building.id);

        // Hexagon path
        const path = this.createHexagonPath(cx, cy, size);
        path.classList.add('hexagon-path');
        group.appendChild(path);

        // Icon/Emoji
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', cx);
        text.setAttribute('y', cy - 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.style.fontSize = '24px';
        text.textContent = building.icon;
        group.appendChild(text);

        // Label
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.classList.add('hexagon-label');
        label.setAttribute('x', cx);
        label.setAttribute('y', cy + 20);
        label.textContent = building.name.replace('Building ', 'B');
        group.appendChild(label);

        // Status indicator
        const statusCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        statusCircle.classList.add('hexagon-status-indicator');
        statusCircle.setAttribute('cx', cx + size - 15);
        statusCircle.setAttribute('cy', cy - size + 15);
        statusCircle.setAttribute('r', '6');
        group.appendChild(statusCircle);

        // Event listeners
        group.addEventListener('mouseenter', (e) => this.showTooltip(building, e));
        group.addEventListener('mouseleave', () => this.hideTooltip());
        group.addEventListener('click', () => this.selectBuilding(building));

        this.svg.appendChild(group);
    }

    createHexagonPath(cx, cy, size) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const angle = Math.PI / 3;
        let pathData = 'M';

        for (let i = 0; i < 6; i++) {
            const x = cx + size * Math.cos(angle * i);
            const y = cy + size * Math.sin(angle * i);
            pathData += `${i === 0 ? '' : ' L'}${x},${y}`;
        }
        pathData += ' Z';

        path.setAttribute('d', pathData);
        return path;
    }

    showTooltip(building, event) {
        const statusClass = `status-${building.status}`;
        const statusText = building.status.charAt(0).toUpperCase() + building.status.slice(1);

        this.tooltip.innerHTML = `
            <div class="tooltip-header">
                <div class="tooltip-icon ${statusClass}">${building.icon}</div>
                <div class="tooltip-title">
                    <div class="tooltip-building-name">${building.name}</div>
                    <div class="tooltip-building-id">${building.type}</div>
                </div>
            </div>
            <div class="tooltip-content">
                <div class="tooltip-stat">
                    <span class="tooltip-stat-label">Status:</span>
                    <span class="tooltip-stat-value">${statusText}</span>
                </div>
                <div class="tooltip-stat">
                    <span class="tooltip-stat-label">Sensors:</span>
                    <span class="tooltip-stat-value">${building.activeSensors}/${building.sensors}</span>
                </div>
                ${building.alerts > 0 ? `
                    <div class="tooltip-stat">
                        <span class="tooltip-stat-label">Alerts:</span>
                        <span class="tooltip-stat-value">${building.alerts}</span>
                    </div>
                ` : ''}
                <div class="tooltip-stat">
                    <span class="tooltip-stat-label">Updated:</span>
                    <span class="tooltip-stat-value">${building.lastUpdate}</span>
                </div>
            </div>
        `;

        const rect = event.target.getBoundingClientRect();
        const containerRect = this.container.querySelector('.honeycomb-map').getBoundingClientRect();
        
        this.tooltip.style.left = `${rect.left - containerRect.left + rect.width / 2}px`;
        this.tooltip.style.top = `${rect.top - containerRect.top - 10}px`;
        this.tooltip.style.transform = 'translateX(-50%) translateY(-100%)';
        this.tooltip.classList.add('visible');
    }

    hideTooltip() {
        this.tooltip.classList.remove('visible');
    }

    selectBuilding(building) {
        // Remove previous selection
        this.svg.querySelectorAll('.hexagon-cell').forEach(cell => {
            cell.classList.remove('selected');
        });

        // Add selection to clicked building
        const cell = this.svg.querySelector(`[data-building-id="${building.id}"]`);
        if (cell) {
            cell.classList.add('selected');
        }

        this.selectedBuilding = building;
        this.renderBuildingDetails(building);
    }

    renderBuildingDetails(building) {
        const detailsContainer = document.getElementById('building-details');
        const statusClass = `status-${building.status}`;
        const statusText = building.status.charAt(0).toUpperCase() + building.status.slice(1);

        detailsContainer.innerHTML = `
            <div class="building-details">
                <div class="detail-section">
                    <div class="detail-section-title">Building Information</div>
                    <div class="detail-card">
                        <div class="detail-card-header">
                            <div class="detail-card-title">${building.name}</div>
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </div>
                        <div class="detail-card-body">
                            <div class="detail-row">
                                <span class="detail-label">Type:</span>
                                <span class="detail-value">${building.type}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Total Sensors:</span>
                                <span class="detail-value">${building.sensors}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Active Sensors:</span>
                                <span class="detail-value">${building.activeSensors}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Active Alerts:</span>
                                <span class="detail-value">${building.alerts}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="detail-section">
                    <div class="detail-section-title">Environmental Data</div>
                    <div class="detail-card">
                        <div class="detail-card-body">
                            <div class="detail-row">
                                <span class="detail-label">Temperature:</span>
                                <span class="detail-value">${building.temperature}°C</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Humidity:</span>
                                <span class="detail-value">${building.humidity}%</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Last Update:</span>
                                <span class="detail-value">${building.lastUpdate}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <button class="btn btn-primary w-full" onclick="window.location.href='/building/${building.id}'">
                    <i class="fas fa-external-link-alt"></i>
                    View Full Details
                </button>
            </div>
        `;
    }

    renderEmptyState() {
        if (this.selectedBuilding) return;
        
        const detailsContainer = document.getElementById('building-details');
        detailsContainer.innerHTML = `
            <div class="building-empty">
                <div class="building-empty-icon">🏢</div>
                <div class="building-empty-text">
                    Select a building on the map to view detailed information
                </div>
            </div>
        `;
    }

    loadBuildings(buildings) {
        this.buildings = buildings;
        this.render();
    }

    updateBuildingStatus(buildingId, status) {
        const building = this.buildings.find(b => b.id === buildingId);
        if (building) {
            building.status = status;
            this.render();
        }
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('honeycomb-map-container');
    if (container) {
        window.honeycombMap = new HoneycombMap('honeycomb-map-container');
    }
});
