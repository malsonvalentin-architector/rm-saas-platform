#!/usr/bin/env python
"""
EMERGENCY FIX SCRIPT - Run this directly on Railway to fix test users immediately.

USAGE ON RAILWAY:
1. Open Railway Dashboard
2. Go to your service
3. Open Shell/Console
4. Run: python emergency_fix_users.py

This script will:
- Create/update ProMonitor Demo company
- Fix admin@promonitor.kz password to Admin123!
- Assign manager@promonitor.kz to company
- Assign client@promonitor.kz to company
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rm.settings')

try:
    django.setup()
except Exception as e:
    print(f"ERROR setting up Django: {e}")
    sys.exit(1)

# Now we can import Django models
from django.utils import timezone
from datetime import timedelta
from data.models import User_profile, Company

def main():
    print("=" * 80)
    print("🚨 EMERGENCY FIX: Updating test users...")
    print("=" * 80)
    print()

    # Step 1: Get or create demo company
    try:
        demo_company, created = Company.objects.get_or_create(
            name='ProMonitor Demo',
            defaults={
                'address': 'Demo Address, Almaty, Kazakhstan',
                'contact_email': 'demo@promonitor.kz',
                'contact_phone': '+7 (777) 000-00-00',
                'subscription_status': 'active',
                'subscription_end_date': timezone.now().date() + timedelta(days=365),
                'is_active': True
            }
        )
        
        if created:
            print(f'✓ Created demo company: {demo_company.name} (ID: {demo_company.id})')
        else:
            print(f'✓ Found existing demo company: {demo_company.name} (ID: {demo_company.id})')
    except Exception as e:
        print(f'✗ ERROR creating/getting company: {e}')
        sys.exit(1)

    print()

    # Step 2: Fix admin@promonitor.kz password
    try:
        admin_user = User_profile.objects.get(email='admin@promonitor.kz')
        admin_user.set_password('Admin123!')
        admin_user.company = demo_company
        admin_user.role = 'admin'
        admin_user.save()
        print(f'✓ FIXED: admin@promonitor.kz')
        print(f'  - Password changed to: Admin123!')
        print(f'  - Company: {demo_company.name}')
        print(f'  - Role: {admin_user.role}')
    except User_profile.DoesNotExist:
        print('✗ admin@promonitor.kz not found!')
    except Exception as e:
        print(f'✗ ERROR fixing admin: {e}')

    # Step 3: Fix manager@promonitor.kz
    try:
        manager_user = User_profile.objects.get(email='manager@promonitor.kz')
        manager_user.company = demo_company
        manager_user.role = 'manager'
        manager_user.save()
        print(f'✓ FIXED: manager@promonitor.kz')
        print(f'  - Company: {demo_company.name}')
        print(f'  - Role: {manager_user.role}')
    except User_profile.DoesNotExist:
        # Create if doesn't exist
        try:
            manager_user = User_profile.objects.create(
                email='manager@promonitor.kz',
                username='manager',
                first_name='Manager',
                last_name='User',
                role='manager',
                company=demo_company,
                is_active=True
            )
            manager_user.set_password('Manager123!')
            manager_user.save()
            print(f'✓ CREATED: manager@promonitor.kz')
            print(f'  - Password: Manager123!')
            print(f'  - Company: {demo_company.name}')
        except Exception as e:
            print(f'✗ ERROR creating manager: {e}')
    except Exception as e:
        print(f'✗ ERROR fixing manager: {e}')

    # Step 4: Fix client@promonitor.kz
    try:
        client_user = User_profile.objects.get(email='client@promonitor.kz')
        client_user.company = demo_company
        client_user.role = 'client'
        client_user.save()
        print(f'✓ FIXED: client@promonitor.kz')
        print(f'  - Company: {demo_company.name}')
        print(f'  - Role: {client_user.role}')
    except User_profile.DoesNotExist:
        # Create if doesn't exist
        try:
            client_user = User_profile.objects.create(
                email='client@promonitor.kz',
                username='client',
                first_name='Client',
                last_name='User',
                role='client',
                company=demo_company,
                is_active=True
            )
            client_user.set_password('Client123!')
            client_user.save()
            print(f'✓ CREATED: client@promonitor.kz')
            print(f'  - Password: Client123!')
            print(f'  - Company: {demo_company.name}')
        except Exception as e:
            print(f'✗ ERROR creating client: {e}')
    except Exception as e:
        print(f'✗ ERROR fixing client: {e}')

    print()
    print("=" * 80)
    print("✅ EMERGENCY FIX COMPLETED!")
    print("=" * 80)
    print()
    
    # Summary
    print("UPDATED CREDENTIALS:")
    print("-" * 80)
    print(f"  admin@promonitor.kz    | Password: Admin123!    | Company: {demo_company.name}")
    print(f"  manager@promonitor.kz  | Password: Manager123!  | Company: {demo_company.name}")
    print(f"  client@promonitor.kz   | Password: Client123!   | Company: {demo_company.name}")
    print("-" * 80)
    print()
    print("🎉 Try logging in now at https://www.promonitor.kz/login/")
    print()

if __name__ == '__main__':
    main()
