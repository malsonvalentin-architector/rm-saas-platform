"""
ProMonitor V2 - AI Assistant Backend
GPT-4 powered monitoring assistant with smart building analysis
"""

import json
from datetime import datetime, timedelta

# Conditional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False
from django.conf import settings
from django.utils import timezone
from data.models import Obj as Building, System as SensorSystem, Atributes as Sensor, Data as SensorReading, AlertEvent as Alert
from .utils import get_building_status, get_company_overview, calculate_sensor_health


class ProMonitorAIAssistant:
    """
    AI Assistant for ProMonitor - GPT-4 powered building monitoring expert
    """
    
    def __init__(self, user):
        self.user = user
        self.company = user.company
        
        # Initialize OpenAI (will use API key when provided)
        # For now, we'll create intelligent responses without actual GPT-4
        self.gpt_available = (
            OPENAI_AVAILABLE and 
            hasattr(settings, 'OPENAI_API_KEY') and 
            settings.OPENAI_API_KEY
        )
        
        if self.gpt_available and openai:
            openai.api_key = settings.OPENAI_API_KEY
    
    def process_message(self, message, context=None, history=None):
        """
        Process user message and generate AI response
        """
        # Analyze message intent
        intent = self.analyze_intent(message)
        
        # Get relevant data based on intent
        data = self.gather_relevant_data(intent, context)
        
        # Generate response
        if self.gpt_available:
            response = self.generate_gpt_response(message, data, history)
        else:
            response = self.generate_smart_response(message, intent, data)
        
        return {
            'message': response['text'],
            'timestamp': datetime.now().isoformat(),
            'confidence': response.get('confidence', 0.9),
            'actions': response.get('actions', []),
            'intent': intent,
            'data_used': response.get('data_sources', [])
        }
    
    def analyze_intent(self, message):
        """
        Analyze user message to determine intent
        """
        message_lower = message.lower()
        
        # Intent patterns
        intents = {
            'status_check': [
                'статус', 'состояние', 'работает', 'здоровье системы', 'overview',
                'show status', 'system health', 'как дела'
            ],
            'alerts_query': [
                'алерт', 'тревог', 'проблем', 'критич', 'warning', 'alert',
                'что не так', 'ошибки', 'сбои'
            ],
            'temperature_analysis': [
                'температур', 'temperature', 'тепло', 'холодно', 'градус',
                'temp', 'климат'
            ],
            'humidity_analysis': [
                'влажность', 'humidity', 'сухо', 'влага'
            ],
            'building_specific': [
                'здание', 'офис', 'склад', 'building', 'помещение'
            ],
            'sensor_query': [
                'датчик', 'sensor', 'показания', 'измерения', 'данные'
            ],
            'analytics_request': [
                'анализ', 'analytics', 'тренд', 'график', 'статистика',
                'за период', 'динамика'
            ],
            'recommendations': [
                'рекомендаци', 'советы', 'как улучшить', 'оптимизация',
                'энергосбережение', 'recommendations'
            ],
            'help_request': [
                'помощь', 'help', 'что можешь', 'команды', 'как пользоваться'
            ]
        }
        
        # Score each intent
        intent_scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent or 'general' if none found
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def gather_relevant_data(self, intent, context=None):
        """
        Gather relevant data based on intent and context
        """
        data = {
            'company_overview': get_company_overview(self.company),
            'timestamp': timezone.now()
        }
        
        # Get buildings data
        buildings = Building.objects.filter(company=self.company)
        data['buildings'] = []
        
        for building in buildings:
            building_data = {
                'id': building.id,
                'name': building.obj,
                'status': get_building_status(building),
                'sensors': [],
                'recent_alerts': []
            }
            
            # Get sensors for this building
            sensors = Sensor.objects.filter(sys__obj=building)[:10]  # Limit for performance
            for sensor in sensors:
                latest_reading = SensorReading.objects.filter(
                    name=sensor
                ).order_by('-date').first()
                
                building_data['sensors'].append({
                    'name': sensor.name,
                    'value': latest_reading.value if latest_reading else None,
                    'unit': sensor.uom,
                    'status': calculate_sensor_health(sensor),
                    'last_update': latest_reading.date if latest_reading else None
                })
            
            # Get recent alerts for this building
            recent_alerts = Alert.objects.filter(
                rule__attribute__sys__obj=building,
                triggered_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-triggered_at')[:5]
            
            for alert in recent_alerts:
                building_data['recent_alerts'].append({
                    'status': alert.status,
                    'triggered_at': alert.triggered_at,
                    'value': alert.value,
                    'sensor_name': alert.rule.attribute.name
                })
            
            data['buildings'].append(building_data)
        
        # Intent-specific data gathering
        if intent == 'temperature_analysis':
            data['temperature_data'] = self.get_temperature_analysis()
        elif intent == 'humidity_analysis':
            data['humidity_data'] = self.get_humidity_analysis()
        elif intent == 'alerts_query':
            data['detailed_alerts'] = self.get_detailed_alerts()
        elif intent == 'analytics_request':
            data['analytics'] = self.get_analytics_data()
        
        return data
    
    def get_temperature_analysis(self):
        """Get temperature-specific analysis"""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        temp_readings = SensorReading.objects.filter(
            name__sys__obj__company=self.company,
            name__name__icontains='temperature',
            date__gte=last_24h
        ).order_by('-date')[:100]
        
        if not temp_readings:
            return None
        
        temps = [float(r.value) for r in temp_readings]
        return {
            'current_avg': sum(temps) / len(temps),
            'min_temp': min(temps),
            'max_temp': max(temps),
            'readings_count': len(temps),
            'trend': 'stable'  # TODO: Calculate actual trend
        }
    
    def get_humidity_analysis(self):
        """Get humidity-specific analysis"""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        humidity_readings = SensorReading.objects.filter(
            name__sys__obj__company=self.company,
            name__name__icontains='humidity',
            date__gte=last_24h
        ).order_by('-date')[:100]
        
        if not humidity_readings:
            return None
        
        humidity_values = [float(r.value) for r in humidity_readings]
        return {
            'current_avg': sum(humidity_values) / len(humidity_values),
            'min_humidity': min(humidity_values),
            'max_humidity': max(humidity_values),
            'readings_count': len(humidity_values)
        }
    
    def get_detailed_alerts(self):
        """Get detailed alerts information"""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        alerts = Alert.objects.filter(
            rule__attribute__sys__obj__company=self.company,
            triggered_at__gte=last_24h
        ).select_related(
            'rule', 'rule__attribute', 'rule__attribute__sys', 'rule__attribute__sys__obj'
        ).order_by('-triggered_at')
        
        alert_data = {
            'total_count': alerts.count(),
            'active_count': alerts.filter(status='active').count(),
            'resolved_count': alerts.filter(status='resolved').count(),
            'by_building': {},
            'recent_alerts': []
        }
        
        # Group by building
        for alert in alerts[:20]:  # Limit for performance
            building_name = alert.rule.attribute.sys.obj.obj
            if building_name not in alert_data['by_building']:
                alert_data['by_building'][building_name] = 0
            alert_data['by_building'][building_name] += 1
            
            alert_data['recent_alerts'].append({
                'building': building_name,
                'sensor': alert.rule.attribute.name,
                'status': alert.status,
                'value': alert.value,
                'triggered_at': alert.triggered_at.strftime('%H:%M')
            })
        
        return alert_data
    
    def get_analytics_data(self):
        """Get analytics data for the last 24 hours"""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # Reading counts by hour
        readings_by_hour = {}
        for hour in range(24):
            hour_start = now - timedelta(hours=hour+1)
            hour_end = now - timedelta(hours=hour)
            
            count = SensorReading.objects.filter(
                name__sys__obj__company=self.company,
                date__gte=hour_start,
                date__lt=hour_end
            ).count()
            
            readings_by_hour[f"{hour_start.hour:02d}:00"] = count
        
        return {
            'readings_by_hour': readings_by_hour,
            'total_readings_24h': sum(readings_by_hour.values()),
            'active_sensors': Sensor.objects.filter(sys__obj__company=self.company).count(),
            'active_buildings': Building.objects.filter(company=self.company).count()
        }
    
    def generate_smart_response(self, message, intent, data):
        """
        Generate intelligent response without GPT-4 (fallback mode)
        """
        responses = {
            'status_check': self.generate_status_response(data),
            'alerts_query': self.generate_alerts_response(data),
            'temperature_analysis': self.generate_temperature_response(data),
            'humidity_analysis': self.generate_humidity_response(data),
            'building_specific': self.generate_building_response(data),
            'sensor_query': self.generate_sensor_response(data),
            'analytics_request': self.generate_analytics_response(data),
            'recommendations': self.generate_recommendations_response(data),
            'help_request': self.generate_help_response()
        }
        
        if intent in responses:
            return responses[intent]
        else:
            return self.generate_general_response(data)
    
    def generate_status_response(self, data):
        """Generate system status response"""
        overview = data['company_overview']
        buildings = data['buildings']
        
        status_counts = overview['building_statuses']
        total_buildings = overview['total_buildings']
        
        response = f"📊 **Общий статус системы:**\n\n"
        response += f"🏢 **Зданий:** {total_buildings}\n"
        response += f"📡 **Датчиков:** {overview['total_sensors']}\n"
        response += f"⚡ **Активных алертов:** {overview['active_alerts']}\n"
        response += f"📈 **Аптайм системы:** {overview['system_uptime']:.1f}%\n\n"
        
        response += "**Статус зданий:**\n"
        if status_counts['healthy'] > 0:
            response += f"✅ Норма: {status_counts['healthy']}\n"
        if status_counts['warning'] > 0:
            response += f"⚠️ Предупреждения: {status_counts['warning']}\n"
        if status_counts['critical'] > 0:
            response += f"🚨 Критичные: {status_counts['critical']}\n"
        if status_counts['offline'] > 0:
            response += f"📴 Офлайн: {status_counts['offline']}\n"
        
        if overview['avg_temperature']:
            response += f"\n🌡️ **Средняя температура:** {overview['avg_temperature']}°C"
        if overview['avg_humidity']:
            response += f"\n💧 **Средняя влажность:** {overview['avg_humidity']}%"
        
        actions = []
        if status_counts['critical'] > 0:
            actions.append({
                'type': 'highlight_critical',
                'message': 'Обратите внимание на критичные здания'
            })
        
        return {
            'text': response,
            'confidence': 0.95,
            'actions': actions,
            'data_sources': ['company_overview', 'buildings']
        }
    
    def generate_alerts_response(self, data):
        """Generate alerts analysis response"""
        if 'detailed_alerts' not in data:
            return {
                'text': "Собираю информацию об алертах...",
                'confidence': 0.7
            }
        
        alerts = data['detailed_alerts']
        
        if alerts['total_count'] == 0:
            return {
                'text': "🎉 **Отлично! Активных алертов нет.**\n\nВаша система работает стабильно. Все показатели в норме.",
                'confidence': 0.9
            }
        
        response = f"🚨 **Анализ алертов за последние 24 часа:**\n\n"
        response += f"📊 **Всего:** {alerts['total_count']}\n"
        response += f"🔴 **Активных:** {alerts['active_count']}\n"
        response += f"✅ **Решено:** {alerts['resolved_count']}\n\n"
        
        if alerts['by_building']:
            response += "**По зданиям:**\n"
            for building, count in sorted(alerts['by_building'].items(), key=lambda x: x[1], reverse=True):
                response += f"• {building}: {count} алертов\n"
        
        if alerts['recent_alerts']:
            response += "\n**Последние алерты:**\n"
            for alert in alerts['recent_alerts'][:5]:
                status_icon = "🔴" if alert['status'] == 'active' else "🟡" if alert['status'] == 'acknowledged' else "✅"
                response += f"{status_icon} {alert['building']} - {alert['sensor']} ({alert['triggered_at']})\n"
        
        return {
            'text': response,
            'confidence': 0.9,
            'data_sources': ['detailed_alerts']
        }
    
    def generate_temperature_response(self, data):
        """Generate temperature analysis response"""
        if 'temperature_data' not in data or not data['temperature_data']:
            return {
                'text': "🌡️ К сожалению, данные о температуре сейчас недоступны. Проверьте подключение датчиков температуры.",
                'confidence': 0.8
            }
        
        temp_data = data['temperature_data']
        
        response = f"🌡️ **Анализ температуры за последние 24 часа:**\n\n"
        response += f"📊 **Средняя температура:** {temp_data['current_avg']:.1f}°C\n"
        response += f"🥶 **Минимум:** {temp_data['min_temp']:.1f}°C\n"
        response += f"🥵 **Максимум:** {temp_data['max_temp']:.1f}°C\n"
        response += f"📈 **Показаний:** {temp_data['readings_count']}\n\n"
        
        # Analysis
        avg_temp = temp_data['current_avg']
        if avg_temp < 18:
            response += "❄️ **Рекомендация:** Температура ниже комфортной. Рассмотрите увеличение отопления."
        elif avg_temp > 26:
            response += "🔥 **Рекомендация:** Температура выше комфортной. Рассмотрите включение кондиционирования."
        else:
            response += "✅ **Температура в комфортном диапазоне** (18-26°C)"
        
        return {
            'text': response,
            'confidence': 0.9,
            'data_sources': ['temperature_data']
        }
    
    def generate_humidity_response(self, data):
        """Generate humidity analysis response"""
        if 'humidity_data' not in data or not data['humidity_data']:
            return {
                'text': "💧 К сожалению, данные о влажности сейчас недоступны. Проверьте подключение датчиков влажности.",
                'confidence': 0.8
            }
        
        humidity_data = data['humidity_data']
        
        response = f"💧 **Анализ влажности за последние 24 часа:**\n\n"
        response += f"📊 **Средняя влажность:** {humidity_data['current_avg']:.1f}%\n"
        response += f"📉 **Минимум:** {humidity_data['min_humidity']:.1f}%\n"
        response += f"📈 **Максимум:** {humidity_data['max_humidity']:.1f}%\n"
        response += f"📊 **Показаний:** {humidity_data['readings_count']}\n\n"
        
        # Analysis
        avg_humidity = humidity_data['current_avg']
        if avg_humidity < 30:
            response += "🏜️ **Внимание:** Воздух слишком сухой. Рекомендуется увлажнение."
        elif avg_humidity > 70:
            response += "🌊 **Внимание:** Воздух слишком влажный. Рекомендуется осушение."
        else:
            response += "✅ **Влажность в комфортном диапазоне** (30-70%)"
        
        return {
            'text': response,
            'confidence': 0.9,
            'data_sources': ['humidity_data']
        }
    
    def generate_help_response(self):
        """Generate help response"""
        response = """🤖 **Я ваш AI помощник ProMonitor! Вот что я умею:**

**📊 Анализ системы:**
• "Покажи статус всех зданий"
• "Есть ли проблемы в системе?"
• "Как работает система?"

**🚨 Управление алертами:**
• "Покажи все алерты"
• "Есть ли критические проблемы?"
• "Что требует внимания?"

**🌡️ Анализ данных:**
• "Анализируй температуру"
• "Проверь влажность"
• "Покажи данные датчиков"

**📈 Аналитика:**
• "Покажи статистику за сутки"
• "Проанализируй тренды"
• "Как изменились показатели?"

**💡 Рекомендации:**
• "Дай советы по оптимизации"
• "Как сэкономить энергию?"
• "Что можно улучшить?"

Просто задавайте вопросы естественным языком! 😊"""
        
        return {
            'text': response,
            'confidence': 1.0
        }
    
    def generate_general_response(self, data):
        """Generate general response"""
        return {
            'text': "Понял ваш вопрос! Я могу помочь с анализом зданий, датчиков и системы мониторинга. Что конкретно вас интересует?",
            'confidence': 0.6
        }
    
    def generate_gpt_response(self, message, data, history):
        """
        Generate response using GPT-4 (when API key is available)
        """
        # TODO: Implement actual GPT-4 integration
        # This would be implemented when OpenAI API key is provided
        system_prompt = self.build_system_prompt(data)
        
        # For now, fallback to smart response
        return self.generate_smart_response(message, self.analyze_intent(message), data)
    
    def build_system_prompt(self, data):
        """
        Build system prompt for GPT-4 with current context
        """
        prompt = f"""You are ProMonitor AI Assistant, an expert in building monitoring and IoT systems.

Current company data:
- Total buildings: {data['company_overview']['total_buildings']}
- Total sensors: {data['company_overview']['total_sensors']}
- Active alerts: {data['company_overview']['active_alerts']}
- System uptime: {data['company_overview']['system_uptime']:.1f}%

Respond in Russian, be helpful and professional. Provide actionable insights.
Use emojis appropriately. Format important information with **bold** text.
"""
        return prompt