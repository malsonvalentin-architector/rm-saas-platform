-- 🔥 NUCLEAR CLEAN: Полная очистка demo данных
-- ВНИМАНИЕ: Удаляет ВСЕ объекты, системы, датчики и данные!

\echo '🚨 NUCLEAR CLEAN INITIATED'
\echo 'Удаление ВСЕХ demo данных из БД...'
\echo ''

-- Отключить FK constraints для быстроты
SET session_replication_role = 'replica';

\echo '1️⃣ Удаление Data (показания датчиков)...'
DELETE FROM data_data;
SELECT 'Удалено Data: ' || COUNT(*) FROM data_data;

\echo '2️⃣ Удаление Atribute (датчики)...'
DELETE FROM data_atribute;
SELECT 'Удалено Atribute: ' || COUNT(*) FROM data_atribute;

\echo '3️⃣ Удаление System (системы)...'
DELETE FROM data_system;
SELECT 'Удалено System: ' || COUNT(*) FROM data_system;

\echo '4️⃣ Удаление Obj (объекты)...'
DELETE FROM data_obj;
SELECT 'Удалено Obj: ' || COUNT(*) FROM data_obj;

-- Включить FK constraints обратно
SET session_replication_role = 'origin';

\echo ''
\echo '✅ NUCLEAR CLEAN COMPLETE'
\echo 'База данных полностью очищена от demo объектов'
\echo ''
\echo '📊 Финальный count:'
SELECT 'Obj: ' || COUNT(*) FROM data_obj;
SELECT 'System: ' || COUNT(*) FROM data_system;
SELECT 'Atribute: ' || COUNT(*) FROM data_atribute;
SELECT 'Data: ' || COUNT(*) FROM data_data;

\echo ''
\echo '🎯 Следующий шаг: railway run python manage.py reset_demo_data'
