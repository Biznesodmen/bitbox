-- Получить всех пациентов
SELECT * FROM patients;

-- Добавить нового пациента
INSERT INTO patients (full_name, diagnosis) 
VALUES ('Сидоров', 'ОРВИ');

-- Обновить диагноз пациента с id=1
UPDATE patients 
SET diagnosis = 'Грипп' 
WHERE id = 1;

-- Удалить пациента с id=3
DELETE FROM patients 
WHERE id = 3;
