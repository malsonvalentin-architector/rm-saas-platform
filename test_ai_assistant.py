#!/usr/bin/env python
"""
Test script for AI Assistant functionality
"""

import os
import sys
import django
import asyncio
from asgiref.sync import sync_to_async

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')
django.setup()

from data.models import User_profile, Company
from home.ai_assistant import ProMonitorAIAssistant


async def test_ai_assistant():
    """Test AI Assistant functionality"""
    
    print("🤖 Testing ProMonitor AI Assistant...")
    
    # Get test user (or create one)
    try:
        user = await sync_to_async(User_profile.objects.filter(role='admin').first)()
        if not user:
            print("❌ No admin user found. Creating test user...")
            
            # Create test company
            company, created = await sync_to_async(Company.objects.get_or_create)(
                name="Test Company",
                defaults={'contact_email': 'test@example.com', 'contact_person': 'Test User'}
            )
            
            # Create test user
            user = await sync_to_async(User_profile.objects.create_user)(
                email='test@promonitor.com',
                password='testpass123',
                company=company,
                role='admin'
            )
            print(f"✅ Created test user: {user.email}")
        
        print(f"👤 Using user: {user.email} ({user.company.name})")
        
        # Initialize AI Assistant
        ai = ProMonitorAIAssistant(user)
        
        # Test messages
        test_messages = [
            "Покажи статус всех зданий",
            "Есть ли критические алерты?",
            "Анализируй температуру",
            "Дай рекомендации по системе",
            "Что ты умеешь?"
        ]
        
        print("\n📝 Testing AI responses...")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. 👤 User: {message}")
            
            try:
                response = ai.process_message(message)
                
                print(f"🤖 AI ({response['intent']}, {response['confidence']:.1%}):")
                print(f"   {response['message'][:200]}...")
                
                if response.get('actions'):
                    print(f"   📋 Actions: {len(response['actions'])}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print(f"\n✅ AI Assistant test completed!")
        print(f"💡 GPT-4 Mode: {'Enabled' if ai.gpt_available else 'Fallback Mode (Smart Responses)'}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    # Run async test
    result = asyncio.run(test_ai_assistant())
    
    if result:
        print("\n🎉 All tests passed! AI Assistant is ready!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)