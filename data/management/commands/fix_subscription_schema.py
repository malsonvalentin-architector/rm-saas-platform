"""
Management команда для исправления схемы SubscriptionPlan
Добавляет недостающие поля created_at и updated_at
Использование: python manage.py fix_subscription_schema
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Добавляет недостающие поля created_at и updated_at в таблицу data_subscriptionplan'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Исправление схемы SubscriptionPlan...")
        
        with connection.cursor() as cursor:
            # Проверяем и добавляем created_at
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'data_subscriptionplan' 
                AND column_name = 'created_at'
            """)
            
            if not cursor.fetchone():
                self.stdout.write("  → Добавляю колонку created_at...")
                cursor.execute("""
                    ALTER TABLE data_subscriptionplan 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                """)
                self.stdout.write(self.style.SUCCESS("  ✅ created_at добавлена"))
            else:
                self.stdout.write("  ℹ️  created_at уже существует")
            
            # Проверяем и добавляем updated_at
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'data_subscriptionplan' 
                AND column_name = 'updated_at'
            """)
            
            if not cursor.fetchone():
                self.stdout.write("  → Добавляю колонку updated_at...")
                cursor.execute("""
                    ALTER TABLE data_subscriptionplan 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                """)
                self.stdout.write(self.style.SUCCESS("  ✅ updated_at добавлена"))
            else:
                self.stdout.write("  ℹ️  updated_at уже существует")
            
            # Показываем текущие колонки
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'data_subscriptionplan'
                ORDER BY ordinal_position
            """)
            
            self.stdout.write("\n📋 Текущая структура data_subscriptionplan:")
            for row in cursor.fetchall():
                self.stdout.write(f"  • {row[0]:30} {row[1]}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Схема успешно исправлена!"))
        self.stdout.write("\n💡 Теперь можно загрузить тарифы:")
        self.stdout.write("   python manage.py load_subscription_plans")
