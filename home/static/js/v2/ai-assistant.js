/**
 * ProMonitor V2 - AI Assistant Chat Interface
 * Real-time chat with GPT-4 powered monitoring assistant
 */

class AIAssistant {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messageHistory = [];
        this.currentSessionId = this.generateSessionId();
        
        this.init();
    }
    
    init() {
        this.createAssistantUI();
        this.setupEventListeners();
        this.loadMessageHistory();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    createAssistantUI() {
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'ai-assistant-toggle';
        toggleButton.innerHTML = '🤖';
        toggleButton.setAttribute('title', 'AI Assistant');
        
        // Create main assistant container
        const assistantContainer = document.createElement('div');
        assistantContainer.className = 'ai-assistant';
        assistantContainer.innerHTML = `
            <div class="ai-assistant-header">
                <h3 class="assistant-title">
                    <div class="assistant-icon">🤖</div>
                    ProMonitor AI
                </h3>
                <div class="assistant-status">
                    <div class="status-dot"></div>
                    Online & Ready
                </div>
            </div>
            
            <div class="ai-chat-messages" id="chat-messages">
                <div class="welcome-message">
                    <div class="welcome-icon">🤖</div>
                    <h4 class="welcome-title">Привет! Я ваш AI помощник</h4>
                    <p class="welcome-subtitle">
                        Я помогу вам анализировать данные датчиков, находить проблемы 
                        и оптимизировать работу ваших зданий.
                    </p>
                    <div class="welcome-suggestions">
                        <div class="suggestion-item" data-message="Покажи статус всех зданий">
                            📊 Покажи статус всех зданий
                        </div>
                        <div class="suggestion-item" data-message="Есть ли критические алерты?">
                            🚨 Есть ли критические алерты?
                        </div>
                        <div class="suggestion-item" data-message="Анализируй температуру в офисе">
                            🌡️ Анализируй температуру в офисе
                        </div>
                        <div class="suggestion-item" data-message="Дай рекомендации по энергосбережению">
                            💡 Дай рекомендации по энергосбережению
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ai-chat-input">
                <div class="quick-actions">
                    <div class="quick-actions-title">Быстрые действия</div>
                    <div class="quick-action-buttons">
                        <button class="quick-action" data-action="status">Статус системы</button>
                        <button class="quick-action" data-action="alerts">Алерты</button>
                        <button class="quick-action" data-action="analytics">Аналитика</button>
                        <button class="quick-action" data-action="help">Помощь</button>
                    </div>
                </div>
                
                <div class="input-container">
                    <textarea 
                        class="message-input" 
                        placeholder="Спросите меня о ваших зданиях и датчиках..."
                        rows="1"
                        id="message-input"
                    ></textarea>
                    <button class="send-button" id="send-button">
                        <span class="material-icons">send</span>
                    </button>
                </div>
            </div>
        `;
        
        // Add to DOM
        document.body.appendChild(toggleButton);
        document.body.appendChild(assistantContainer);
        
        // Store references
        this.toggleButton = toggleButton;
        this.assistantContainer = assistantContainer;
        this.messagesContainer = assistantContainer.querySelector('#chat-messages');
        this.messageInput = assistantContainer.querySelector('#message-input');
        this.sendButton = assistantContainer.querySelector('#send-button');
    }
    
    setupEventListeners() {
        // Toggle button
        this.toggleButton.addEventListener('click', () => this.toggle());
        
        // Send button
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key to send
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 100) + 'px';
        });
        
        // Quick action buttons
        this.assistantContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-action')) {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            }
            
            if (e.target.classList.contains('suggestion-item')) {
                const message = e.target.dataset.message;
                this.messageInput.value = message;
                this.sendMessage();
            }
        });
        
        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.assistantContainer.classList.add('active');
        this.toggleButton.classList.add('active');
        this.toggleButton.innerHTML = '✕';
        
        // Focus input
        setTimeout(() => {
            this.messageInput.focus();
        }, 300);
        
        // Track analytics
        this.trackEvent('assistant_opened');
    }
    
    close() {
        this.isOpen = false;
        this.assistantContainer.classList.remove('active');
        this.toggleButton.classList.remove('active');
        this.toggleButton.innerHTML = '🤖';
        
        // Track analytics
        this.trackEvent('assistant_closed');
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Hide welcome message
        this.hideWelcomeMessage();
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.callAIAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add assistant response
            this.addMessage('assistant', response.message, {
                timestamp: response.timestamp,
                confidence: response.confidence,
                actions: response.actions
            });
            
            // Handle any actions
            if (response.actions && response.actions.length > 0) {
                this.handleAssistantActions(response.actions);
            }
            
        } catch (error) {
            console.error('AI Assistant error:', error);
            
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Извините, произошла ошибка. Попробуйте еще раз.', {
                error: true
            });
        }
        
        // Track analytics
        this.trackEvent('message_sent', { message_length: message.length });
    }
    
    async callAIAPI(message) {
        // Get current context
        const context = await this.getCurrentContext();
        
        const response = await fetch('/dashboard/v2/api/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                message: message,
                session_id: this.currentSessionId,
                context: context,
                history: this.messageHistory.slice(-10) // Last 10 messages
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async getCurrentContext() {
        // Get current dashboard context
        const context = {
            current_page: window.location.pathname,
            selected_building: this.getSelectedBuilding(),
            dashboard_stats: window.dashboardData?.statistics || {},
            user_company: this.getUserCompany(),
            timestamp: new Date().toISOString()
        };
        
        // Add real-time building data if available
        if (window.buildingMap && window.buildingMap.buildings) {
            context.buildings = window.buildingMap.buildings.map(building => ({
                id: building.id,
                name: building.name,
                status: building.status,
                sensor_count: building.sensorCount,
                temperature: building.temperature,
                humidity: building.humidity
            }));
        }
        
        return context;
    }
    
    addMessage(sender, content, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        
        const timestamp = options.timestamp || new Date().toLocaleTimeString('ru', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const bubbleClass = sender === 'user' ? 'user' : 'assistant';
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${sender}">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-bubble ${bubbleClass}">
                    ${this.formatMessage(content)}
                </div>
                <div class="message-time ${sender}">
                    ${timestamp}
                    ${options.confidence ? `(${Math.round(options.confidence * 100)}%)` : ''}
                </div>
                ${options.error ? '<div class="message-status error"><span class="status-icon">⚠️</span>Ошибка</div>' : ''}
                ${sender === 'assistant' ? `
                    <div class="message-actions">
                        <button class="message-action" onclick="aiAssistant.copyMessage(this)">Копировать</button>
                        <button class="message-action" onclick="aiAssistant.rateMessage(this, 'up')">👍</button>
                        <button class="message-action" onclick="aiAssistant.rateMessage(this, 'down')">👎</button>
                    </div>
                ` : ''}
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({
            sender,
            content,
            timestamp: new Date().toISOString(),
            ...options
        });
        
        // Save to localStorage
        this.saveMessageHistory();
    }
    
    formatMessage(content) {
        // Format message with markdown-like syntax
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.sendButton.disabled = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar assistant">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    <span>Думаю...</span>
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.sendButton.disabled = false;
        
        const typingMessage = this.messagesContainer.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }
    
    hideWelcomeMessage() {
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
    }
    
    handleQuickAction(action) {
        const actionMessages = {
            status: 'Покажи общий статус всех систем и зданий',
            alerts: 'Покажи все активные алерты и их критичность',
            analytics: 'Проанализируй данные за последние 24 часа',
            help: 'Что ты можешь делать? Покажи список команд'
        };
        
        const message = actionMessages[action];
        if (message) {
            this.messageInput.value = message;
            this.sendMessage();
        }
    }
    
    handleAssistantActions(actions) {
        actions.forEach(action => {
            switch (action.type) {
                case 'highlight_building':
                    this.highlightBuilding(action.building_id);
                    break;
                case 'show_chart':
                    this.showChart(action.chart_data);
                    break;
                case 'navigate_to':
                    setTimeout(() => {
                        window.location.href = action.url;
                    }, 1000);
                    break;
            }
        });
    }
    
    highlightBuilding(buildingId) {
        if (window.buildingMap) {
            window.buildingMap.selectBuilding(buildingId);
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    copyMessage(button) {
        const messageContent = button.closest('.message-content').querySelector('.message-bubble').textContent;
        navigator.clipboard.writeText(messageContent).then(() => {
            button.textContent = 'Скопировано!';
            setTimeout(() => {
                button.textContent = 'Копировать';
            }, 2000);
        });
    }
    
    rateMessage(button, rating) {
        // Send rating to backend
        fetch('/dashboard/v2/api/ai-rate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                session_id: this.currentSessionId,
                rating: rating,
                message_index: this.messageHistory.length - 1
            })
        });
        
        // Visual feedback
        button.style.opacity = '0.5';
        button.disabled = true;
    }
    
    loadMessageHistory() {
        const saved = localStorage.getItem('ai_assistant_history');
        if (saved) {
            try {
                this.messageHistory = JSON.parse(saved);
                
                // Restore messages if any
                if (this.messageHistory.length > 0) {
                    this.hideWelcomeMessage();
                    this.messageHistory.forEach(msg => {
                        this.addMessage(msg.sender, msg.content, {
                            timestamp: new Date(msg.timestamp).toLocaleTimeString('ru', {
                                hour: '2-digit',
                                minute: '2-digit'
                            }),
                            skipHistory: true
                        });
                    });
                }
            } catch (e) {
                console.warn('Failed to load message history:', e);
            }
        }
    }
    
    saveMessageHistory() {
        try {
            localStorage.setItem('ai_assistant_history', JSON.stringify(this.messageHistory));
        } catch (e) {
            console.warn('Failed to save message history:', e);
        }
    }
    
    clearHistory() {
        this.messageHistory = [];
        localStorage.removeItem('ai_assistant_history');
        this.messagesContainer.innerHTML = '';
        location.reload(); // Reload to show welcome message
    }
    
    getCSRFToken() {
        const cookie = document.cookie.split(';')
            .find(cookie => cookie.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
    
    getSelectedBuilding() {
        if (window.buildingMap && window.buildingMap.selectedBuilding) {
            return window.buildingMap.selectedBuilding.building;
        }
        return null;
    }
    
    getUserCompany() {
        // Extract from DOM or global data
        return {
            name: document.querySelector('.company-name')?.textContent || 'Unknown Company'
        };
    }
    
    trackEvent(event, data = {}) {
        // Analytics tracking
        if (window.gtag) {
            window.gtag('event', event, {
                event_category: 'ai_assistant',
                ...data
            });
        }
        
        console.log('AI Assistant Event:', event, data);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on dashboard v2
    if (document.querySelector('.dashboard-container')) {
        window.aiAssistant = new AIAssistant();
        
        // Global helper functions
        window.clearAIHistory = () => window.aiAssistant.clearHistory();
        
        console.log('🤖 AI Assistant initialized');
    }
});

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIAssistant;
}