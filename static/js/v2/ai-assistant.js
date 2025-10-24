/**
 * ProMonitor V2 - AI Assistant Chat Client
 * Full-featured chat interface with real-time capabilities
 */

class AIAssistant {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        
        this.init();
    }

    init() {
        this.loadFromStorage();
        this.createChatUI();
        this.attachEventListeners();
        
        if (this.messages.length === 0) {
            this.addWelcomeMessage();
        }
    }

    generateSessionId() {
        return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem('ai-chat-messages');
            if (stored) {
                this.messages = JSON.parse(stored);
            }
        } catch (e) {
            console.error('Failed to load chat history:', e);
        }
    }

    saveToStorage() {
        try {
            localStorage.setItem('ai-chat-messages', JSON.stringify(this.messages));
        } catch (e) {
            console.error('Failed to save chat history:', e);
        }
    }

    createChatUI() {
        const chatHTML = `
            <button class="ai-chat-toggle" id="ai-chat-toggle" title="Open AI Assistant">
                <i class="fas fa-robot"></i>
            </button>
            
            <div class="ai-chat-container" id="ai-chat-container">
                <div class="ai-chat-header">
                    <div class="ai-chat-title-section">
                        <div class="ai-chat-avatar">🤖</div>
                        <div class="ai-chat-title">
                            <div class="ai-chat-name">ProMonitor AI</div>
                            <div class="ai-chat-status">
                                <span class="status-indicator"></span>
                                Online
                            </div>
                        </div>
                    </div>
                    <div class="ai-chat-actions">
                        <button class="ai-chat-action-btn" id="clear-chat" title="Clear Chat">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="ai-chat-action-btn" id="close-chat" title="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <div class="ai-chat-messages" id="ai-chat-messages"></div>

                <div class="quick-actions" id="quick-actions">
                    <button class="quick-action-btn" data-action="check-alerts">
                        <i class="fas fa-bell"></i> Check Alerts
                    </button>
                    <button class="quick-action-btn" data-action="sensor-status">
                        <i class="fas fa-thermometer-half"></i> Sensor Status
                    </button>
                    <button class="quick-action-btn" data-action="system-health">
                        <i class="fas fa-heart"></i> System Health
                    </button>
                </div>

                <div class="ai-chat-input-container">
                    <div class="ai-chat-input-wrapper">
                        <textarea 
                            class="ai-chat-input" 
                            id="ai-chat-input"
                            placeholder="Ask me anything about your systems..."
                            rows="1"
                        ></textarea>
                        <button class="ai-chat-send-btn" id="ai-chat-send">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
        this.renderMessages();
    }

    attachEventListeners() {
        // Toggle chat
        document.getElementById('ai-chat-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.getElementById('close-chat').addEventListener('click', () => {
            this.closeChat();
        });

        // Clear chat
        document.getElementById('clear-chat').addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all messages?')) {
                this.clearChat();
            }
        });

        // Send message
        document.getElementById('ai-chat-send').addEventListener('click', () => {
            this.sendMessage();
        });

        // Input handlers
        const input = document.getElementById('ai-chat-input');
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        input.addEventListener('input', () => {
            this.autoResizeInput();
        });

        // Quick actions
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('[data-action]').dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const container = document.getElementById('ai-chat-container');
        const toggle = document.getElementById('ai-chat-toggle');
        
        if (this.isOpen) {
            container.classList.add('visible');
            toggle.classList.add('active');
            document.getElementById('ai-chat-input').focus();
        } else {
            container.classList.remove('visible');
            toggle.classList.remove('active');
        }
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('ai-chat-container').classList.remove('visible');
        document.getElementById('ai-chat-toggle').classList.remove('active');
    }

    clearChat() {
        this.messages = [];
        this.saveToStorage();
        this.renderMessages();
        this.addWelcomeMessage();
    }

    autoResizeInput() {
        const input = document.getElementById('ai-chat-input');
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }

    addWelcomeMessage() {
        const welcomeMsg = {
            role: 'assistant',
            content: `Hello! I'm ProMonitor AI Assistant. I can help you with:

• Checking system alerts and sensor status
• Analyzing temperature and environmental data
• Generating reports and insights
• Troubleshooting issues
• Answering questions about your HVAC systems

How can I assist you today?`,
            timestamp: new Date().toISOString()
        };
        
        this.messages.push(welcomeMsg);
        this.saveToStorage();
        this.renderMessages();
    }

    async sendMessage() {
        const input = document.getElementById('ai-chat-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTyping();

        try {
            const response = await this.sendToBackend(message);
            this.hideTyping();
            this.addMessage('assistant', response.message);
        } catch (error) {
            this.hideTyping();
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            console.error('Chat error:', error);
        }
    }

    async sendToBackend(message) {
        const response = await fetch('/api/v2/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId,
                context: {
                    current_page: window.location.pathname,
                    user_agent: navigator.userAgent
                }
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get response from AI');
        }

        return await response.json();
    }

    addMessage(role, content) {
        const message = {
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        };

        this.messages.push(message);
        this.saveToStorage();
        this.renderMessages();
    }

    showTyping() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('ai-chat-messages');
        
        const typingHTML = `
            <div class="typing-indicator" id="typing-indicator">
                <div class="message-avatar">🤖</div>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    renderMessages() {
        const container = document.getElementById('ai-chat-messages');
        container.innerHTML = '';

        this.messages.forEach(msg => {
            const messageHTML = this.createMessageHTML(msg);
            container.insertAdjacentHTML('beforeend', messageHTML);
        });

        this.scrollToBottom();
    }

    createMessageHTML(message) {
        const time = new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const avatar = message.role === 'assistant' ? '🤖' : '👤';
        const formattedContent = this.formatMessage(message.content);

        return `
            <div class="chat-message ${message.role}">
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">
                    <div class="message-bubble">${formattedContent}</div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;
    }

    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/•/g, '&bull;');
    }

    scrollToBottom() {
        setTimeout(() => {
            const container = document.getElementById('ai-chat-messages');
            container.scrollTop = container.scrollHeight;
        }, 100);
    }

    handleQuickAction(action) {
        const actions = {
            'check-alerts': 'Show me all active alerts in the system',
            'sensor-status': 'What is the current status of all sensors?',
            'system-health': 'Give me a system health overview'
        };

        const message = actions[action];
        if (message) {
            document.getElementById('ai-chat-input').value = message;
            this.sendMessage();
        }
    }

    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// Initialize AI Assistant when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.aiAssistant = new AIAssistant();
    });
} else {
    window.aiAssistant = new AIAssistant();
}
