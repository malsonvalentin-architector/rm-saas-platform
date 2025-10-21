-- SQL скрипт для добавления недостающих полей в таблицу data_subscriptionplan
-- Запустить через: python manage.py dbshell < fix_subscriptionplan_schema.sql

BEGIN;

-- Проверяем наличие колонки created_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_subscriptionplan' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE data_subscriptionplan 
        ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        RAISE NOTICE 'Колонка created_at добавлена';
    ELSE
        RAISE NOTICE 'Колонка created_at уже существует';
    END IF;
END $$;

-- Проверяем наличие колонки updated_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'data_subscriptionplan' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE data_subscriptionplan 
        ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        RAISE NOTICE 'Колонка updated_at добавлена';
    ELSE
        RAISE NOTICE 'Колонка updated_at уже существует';
    END IF;
END $$;

COMMIT;

-- Показываем структуру таблицы для проверки
\d data_subscriptionplan;
