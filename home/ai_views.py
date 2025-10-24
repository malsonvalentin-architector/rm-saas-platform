"""
ProMonitor V2 - AI Assistant Django Views
API endpoints for AI chat functionality
"""

import json
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.core.cache import cache
from asgiref.sync import sync_to_async
import logging

from .ai_assistant import ProMonitorAIAssistant
from data.models import User_profile


logger = logging.getLogger(__name__)


@method_decorator([login_required, csrf_exempt], name='dispatch')
class AIChatView(View):
    """
    Main AI Chat API endpoint
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            context = data.get('context', {})
            history = data.get('history', [])
            
            if not message:
                return JsonResponse({
                    'error': 'Message is required'
                }, status=400)
            
            # Rate limiting check
            rate_limit_key = f'ai_chat_rate_limit_{request.user.id}'
            requests_count = cache.get(rate_limit_key, 0)
            
            if requests_count >= 30:  # 30 requests per minute
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please wait a moment.',
                    'retry_after': 60
                }, status=429)
            
            # Increment rate limit counter
            cache.set(rate_limit_key, requests_count + 1, 60)
            
            # Initialize AI Assistant
            ai_assistant = ProMonitorAIAssistant(request.user)
            
            # Process message
            response = ai_assistant.process_message(
                message=message,
                context=context,
                history=history
            )
            
            # Log the interaction (async operation)
            try:
                from data.models import AIInteractionLog
                AIInteractionLog.objects.create(
                    user=request.user,
                    session_id=session_id,
                    message=message,
                    response=response.get('message', ''),
                    intent=response.get('intent', 'unknown'),
                    confidence=response.get('confidence', 0.0),
                    context_data=context,
                    response_data=response,
                    timestamp=timezone.now()
                )
            except Exception as e:
                logger.warning(f"Failed to log AI interaction: {str(e)}")
            
            return JsonResponse(response)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format'
            }, status=400)
            
        except Exception as e:
            logger.error(f"AI Chat error for user {request.user.id}: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'Произошла ошибка. Попробуйте еще раз.'
            }, status=500)
    
    # Removed async log_interaction method


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_rate_message(request):
    """
    Rate AI message (thumbs up/down feedback)
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')  # 'up' or 'down'
        message_index = data.get('message_index', 0)
        
        if rating not in ['up', 'down']:
            return JsonResponse({'error': 'Invalid rating'}, status=400)
        
        # Store rating for future ML training
        cache_key = f'ai_rating_{session_id}_{message_index}'
        cache.set(cache_key, {
            'rating': rating,
            'user_id': request.user.id,
            'timestamp': timezone.now().isoformat()
        }, 86400)  # Store for 24 hours
        
        # TODO: Store in database for long-term analytics
        
        return JsonResponse({
            'success': True,
            'message': 'Спасибо за обратную связь!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"AI rating error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def ai_chat_history(request):
    """
    Get chat history for current user
    """
    try:
        session_id = request.GET.get('session_id')
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 messages
        
        # For now, return empty - history is stored in frontend localStorage
        # TODO: Implement server-side history storage
        
        return JsonResponse({
            'messages': [],
            'session_id': session_id,
            'count': 0
        })
        
    except Exception as e:
        logger.error(f"AI history error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def ai_clear_history(request):
    """
    Clear chat history for current user
    """
    try:
        session_id = request.GET.get('session_id')
        
        # Clear server-side history (when implemented)
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': 'История очищена'
        })
        
    except Exception as e:
        logger.error(f"AI clear history error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["GET"])
def ai_status(request):
    """
    Get AI Assistant status and capabilities
    """
    try:
        from django.conf import settings
        
        # Check if OpenAI is configured
        openai_available = hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY
        
        # Get user's company data for context
        company = request.user.company
        buildings_count = company.obj_set.count() if company else 0
        
        status = {
            'available': True,
            'gpt_enabled': openai_available,
            'capabilities': [
                'Анализ статуса зданий',
                'Мониторинг алертов',
                'Анализ данных датчиков',
                'Рекомендации по оптимизации',
                'Статистика и аналитика'
            ],
            'context': {
                'buildings_count': buildings_count,
                'user_role': request.user.role,
                'company_name': company.name if company else 'Unknown'
            },
            'limits': {
                'messages_per_minute': 30,
                'max_message_length': 1000
            }
        }
        
        return JsonResponse(status)
        
    except Exception as e:
        logger.error(f"AI status error: {str(e)}")
        return JsonResponse({
            'available': False,
            'error': 'Service temporarily unavailable'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_quick_analysis(request):
    """
    Quick AI analysis endpoint for dashboard widgets
    """
    try:
        data = json.loads(request.body)
        analysis_type = data.get('type', 'overview')
        
        ai_assistant = ProMonitorAIAssistant(request.user)
        
        # Generate quick analysis based on type
        if analysis_type == 'overview':
            message = "Дай краткий обзор состояния всех систем"
        elif analysis_type == 'alerts':
            message = "Покажи критичные алерты"
        elif analysis_type == 'trends':
            message = "Анализируй тренды за последние часы"
        else:
            message = "Общий статус системы"
        
        # Use asyncio to run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                ai_assistant.process_message(message)
            )
        finally:
            loop.close()
        
        # Return condensed response for widget
        return JsonResponse({
            'analysis': response['message'][:300] + '...' if len(response['message']) > 300 else response['message'],
            'confidence': response.get('confidence', 0.8),
            'timestamp': response['timestamp'],
            'type': analysis_type
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"AI quick analysis error: {str(e)}")
        return JsonResponse({
            'error': 'Analysis temporarily unavailable',
            'analysis': 'Система работает в штатном режиме.'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_suggestions(request):
    """
    Get AI suggestions based on current context
    """
    try:
        page = request.GET.get('page', 'dashboard')
        building_id = request.GET.get('building_id')
        
        suggestions = []
        
        if page == 'dashboard':
            suggestions = [
                "Покажи статус всех зданий",
                "Есть ли критические алерты?",
                "Анализируй температуру в офисах",
                "Дай рекомендации по энергосбережению",
                "Показатели за последние 24 часа"
            ]
        elif page == 'building' and building_id:
            suggestions = [
                f"Анализируй здание ID {building_id}",
                "Статус датчиков в этом здании",
                "История алертов для здания",
                "Рекомендации по оптимизации",
                "Сравни с другими зданиями"
            ]
        elif page == 'alerts':
            suggestions = [
                "Покажи все активные алерты",
                "Какие алерты самые критичные?",
                "Статистика алертов за неделю",
                "Как часто срабатывают алерты?",
                "Рекомендации по снижению алертов"
            ]
        else:
            suggestions = [
                "Общий статус системы",
                "Что требует внимания?",
                "Помощь по использованию системы"
            ]
        
        return JsonResponse({
            'suggestions': suggestions,
            'page': page,
            'context': {
                'building_id': building_id
            }
        })
        
    except Exception as e:
        logger.error(f"AI suggestions error: {str(e)}")
        return JsonResponse({
            'suggestions': [
                "Покажи статус системы",
                "Есть ли проблемы?",
                "Помощь"
            ]
        })


# WebSocket consumer for real-time AI chat (if using Django Channels)
try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    import json
    
    class AIChatConsumer(AsyncWebsocketConsumer):
        """
        WebSocket consumer for real-time AI chat
        """
        
        async def connect(self):
            self.user = self.scope['user']
            if self.user.is_anonymous:
                await self.close()
                return
            
            self.session_id = self.scope['url_route']['kwargs'].get('session_id', 'default')
            self.group_name = f'ai_chat_{self.user.id}_{self.session_id}'
            
            # Join personal AI chat group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'welcome',
                'message': 'AI Assistant подключен. Готов к общению!'
            }))
        
        async def disconnect(self, close_code):
            # Leave group
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
        
        async def receive(self, text_data):
            try:
                data = json.loads(text_data)
                message_type = data.get('type', 'message')
                
                if message_type == 'message':
                    await self.handle_chat_message(data)
                elif message_type == 'typing':
                    await self.handle_typing_indicator(data)
                
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid message format'
                }))
        
        async def handle_chat_message(self, data):
            message = data.get('message', '').strip()
            if not message:
                return
            
            # Initialize AI Assistant
            ai_assistant = ProMonitorAIAssistant(self.user)
            
            try:
                # Process message
                response = await ai_assistant.process_message(
                    message=message,
                    context=data.get('context', {}),
                    history=data.get('history', [])
                )
                
                # Send response
                await self.send(text_data=json.dumps({
                    'type': 'response',
                    'message': response['message'],
                    'timestamp': response['timestamp'],
                    'confidence': response.get('confidence', 0.9),
                    'actions': response.get('actions', [])
                }))
                
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Произошла ошибка при обработке сообщения.'
                }))
        
        async def handle_typing_indicator(self, data):
            # Broadcast typing indicator to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'typing': data.get('typing', False)
                }
            )
        
        async def typing_indicator(self, event):
            # Send typing indicator to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'typing': event['typing']
            }))

except ImportError:
    # Django Channels not available
    AIChatConsumer = None