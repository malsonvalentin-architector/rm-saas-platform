#!/usr/bin/env python
"""
Simple sync test for AI Assistant
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')
django.setup()

from data.models import User_profile, Company
from home.ai_assistant import ProMonitorAIAssistant


def test_ai_simple():
    """Simple synchronous test"""
    
    print("🤖 Testing ProMonitor AI Assistant (Simple)...")
    
    # Get or create test user
    try:
        user = User_profile.objects.filter(email='test@promonitor.com').first()
        
        if not user:
            print("Creating test user...")
            company, _ = Company.objects.get_or_create(
                name="Test Company",
                defaults={'contact_email': 'test@example.com', 'contact_person': 'Test User'}
            )
            
            user = User_profile.objects.create_user(
                email='test@promonitor.com',
                password='testpass123',
                company=company,
                role='admin'
            )
        
        print(f"👤 User: {user.email}")
        
        # Initialize AI
        ai = ProMonitorAIAssistant(user)
        print(f"💡 GPT Mode: {'Enabled' if ai.gpt_available else 'Smart Fallback'}")
        
        # Test simple message
        print("\n📝 Testing simple message...")
        
        try:
            response = ai.generate_help_response()
            print(f"✅ Help Response: {response['text'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        
        # Test intent analysis
        print("\n🧠 Testing intent analysis...")
        
        test_messages = [
            "Покажи статус зданий",
            "Есть ли алерты?", 
            "Анализируй температуру",
            "Что ты умеешь?"
        ]
        
        for msg in test_messages:
            intent = ai.analyze_intent(msg)
            print(f"  '{msg}' → {intent}")
        
        print("\n🎉 Basic AI tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ai_simple()
    
    if success:
        print("\n✅ AI Assistant is working!")
    else:
        print("\n💥 AI Assistant has issues!")
        exit(1)