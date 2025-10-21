-- ProMonitor Demo Data Cleanup Script
-- Safe deletion of all demo data for ProMonitor Kazakhstan company
-- Run this in Railway PostgreSQL Data tab or via psql

-- Step 1: Find company ID (should be 1 or 2)
SELECT id, name, is_active FROM data_company WHERE name LIKE '%ProMonitor%';

-- Step 2: Count current data (before deletion)
SELECT 
    (SELECT COUNT(*) FROM data_obj WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')) as objects,
    (SELECT COUNT(*) FROM data_system WHERE obj_id IN (SELECT id FROM data_obj WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%'))) as systems,
    (SELECT COUNT(*) FROM data_atributes WHERE sys_id IN (SELECT id FROM data_system WHERE obj_id IN (SELECT id FROM data_obj WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')))) as sensors;

-- Step 3: Delete all data (CAREFUL - THIS IS IRREVERSIBLE!)
-- Uncomment lines below to execute deletion:

-- Delete data points
-- DELETE FROM data_data 
-- WHERE name_id IN (
--     SELECT a.id FROM data_atributes a
--     JOIN data_system s ON a.sys_id = s.id
--     JOIN data_obj o ON s.obj_id = o.id
--     WHERE o.company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')
-- );

-- Delete alert rules
-- DELETE FROM data_alertrule 
-- WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%');

-- Delete sensors (atributes)
-- DELETE FROM data_atributes 
-- WHERE sys_id IN (
--     SELECT s.id FROM data_system s
--     JOIN data_obj o ON s.obj_id = o.id
--     WHERE o.company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')
-- );

-- Delete systems
-- DELETE FROM data_system 
-- WHERE obj_id IN (
--     SELECT id FROM data_obj 
--     WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')
-- );

-- Delete objects
-- DELETE FROM data_obj 
-- WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%');

-- Step 4: Verify deletion
-- SELECT 
--     (SELECT COUNT(*) FROM data_obj WHERE company_id IN (SELECT id FROM data_company WHERE name LIKE '%ProMonitor%')) as remaining_objects;

-- Expected result: remaining_objects = 0
