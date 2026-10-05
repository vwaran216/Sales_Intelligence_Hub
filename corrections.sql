SHOW DATABASES;
USE sales_intelligence_hub;
SHOW TABLES;
SELECT * FROM branches;
SELECT * FROM users;
SELECT*FROM branches;
INSERT INTO users
(username, password, branch_id, role, email)
VALUES
('superadmin', 'admin123', NULL, 'Super Admin', 'superadmin@saleshub.com');

INSERT INTO users
(username, password, branch_id, role, email)
VALUES
('chennaiadmin', 'admin123', 1, 'Admin', 'chennai@saleshub.com');
SELECT * FROM users

USE sales_intelligence_hub;

SELECT username, role, branch_id
FROM users
WHERE username = 'chennaiadmin';

SELECT branch_id, branch_name
FROM branches

UPDATE users
SET branch_id = 1
WHERE username = 'chennaiadmin';

SELECT username, role, branch_id
FROM users
WHERE username = 'chennaiadmin';


USE sales_intelligence_hub;

SELECT *
FROM customer_sales
ORDER BY sale_id DESC
LIMIT 5;

DESCRIBE customer_sales;


SELECT sale_id, name, gross_sales, received_amount, pending_amount, status
FROM customer_sales
ORDER BY sale_id DESC
LIMIT 1;


SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE name = 'Arun Kumar';

SHOW TRIGGERS
WHERE 'Table' = 'payment_splits';

SHOW CREATE TRIGGER
update_received_amount;

USE sales_intelligence_hub;
SHOW TRIGGERS

SHOW CREATE TRIGGER
after_payment_insert;



USE sales_intelligence_hub;

SELECT 
    TRIGGER_NAME,
    ACTION_STATEMENT
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'sales_intelligence_hub'
AND TRIGGER_NAME = 'after_payment_insert';


SELECT ACTION_STATEMENT
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'sales_intelligence_hub'
  AND TRIGGER_NAME = 'after_payment_insert';
  
  
  
  USE sales_intelligence_hub;

DROP TRIGGER IF EXISTS after_payment_insert;

DELIMITER $$

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN

    UPDATE customer_sales
    SET
        received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        status = CASE
            WHEN (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits
                WHERE sale_id = NEW.sale_id
            ) >= gross_sales
            THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;

END$$

DELIMITER ;


SHOW TRIGGERS
WHERE 'Trigger' = 'after_payment_insert';


SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE name = 'Arun Kumar';


SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE name = 'Priya';


USE sales_intelligence_hub;

UPDATE customer_sales
SET status = 'Close'
WHERE name = 'Arun Kumar'
  AND pending_amount = 0;
  
  
  SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE name IN ('Arun Kumar', 'Priya');


SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE name = 'Arun Kumar';


USE sales_intelligence_hub;

UPDATE customer_sales
SET status = 'Close'
WHERE name = 'Arun Kumar'
  AND pending_amount = 0;

SELECT sale_id, name, gross_sales, received_amount, pending_amount, status
FROM customer_sales
WHERE name = 'Arun Kumar';

USE sales_intelligence_hub;

SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status,
    (gross_sales - received_amount) AS calculated_pending
FROM customer_sales
WHERE name = 'Arun Kumar';


USE sales_intelligence_hub;

UPDATE customer_sales
SET status = 'Close'
WHERE name = 'Arun Kumar';

SELECT sale_id, name, gross_sales, received_amount, pending_amount, status
FROM customer_sales
WHERE name = 'Arun Kumar';



USE sales_intelligence_hub;

SELECT
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    ACTION_TIMING,
    EVENT_OBJECT_TABLE
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'sales_intelligence_hub'
  AND EVENT_OBJECT_TABLE = 'customer_sales';
  
  
  
USE sales_intelligence_hub;

UPDATE customer_sales
SET status = 'Close'
WHERE sale_id = 1;

COMMIT;

SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE sale_id = 1;
  
  USE sales_intelligence_hub;
  SHOW CREATE TABLE customer_sales;
  LIKE 'status';
  
  
SELECT 
    sale_id,
    customer_name,
    total_amount,
    received_amount,
    pending_amount,
    status
FROM sales
WHERE customer_name IN ('Priya', 'Arunkumar');

SHOW DATABASES;
USE sales_intelligence_hub;
SHOW TABLES;

SELECT * FROM customer_sales WHERE name IN ('Priya' , 'Arunkumar');  
SELECT * FROM customer_sales WHERE status = 'open';


SHOW TRIGGERS;

SHOW TRIGGERS LIKE 'customer_sales';
SHOW TRIGGERS LIKE 'payment_split';

SHOW CREATE TRIGGER after_payment_insert;
DESCRIBE customer_sales;

DROP TRIGGER after_payment_insert;



DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET
        received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        status = CASE
            WHEN gross_sales - (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits
                WHERE sale_id = NEW.sale_id
            ) <= 0 THEN 'Closed'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END//

DELIMITER ;

DESCRIBE payment_splits;

DROP TRIGGER IF EXISTS after_payment_insert;



DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET
        received_amount = (
            SELECT COALESCE(SUM(Amount Paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(Amount Paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        status = CASE
            WHEN gross_sales - (
                SELECT COALESCE(SUM(Amount Paid), 0)
                FROM payment_splits
                WHERE sale_id = NEW.sale_id
            ) <= 0
            THEN 'Closed'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END//

DELIMITER ;

DESCRIBE customer_sales;



DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET
        received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits
            WHERE sale_id = NEW.sale_id
        ),
        Status = CASE
            WHEN gross_sales - (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits
                WHERE sale_id = NEW.sale_id
            ) <= 0
            THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END//

DELIMITER ;

SELECT
    sale_id,
    name,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE 'name' IN ('Priya','Test_Customer');

SHOW COLUMNS FROM customer_sales;

SELECT sale_id, name, gross_sales, received_amount, pending_amount, status
FROM customer_sales
WHERE name IN ('Priya', 'Test_Customer');


UPDATE customer_sales
SET status = 'Close'
WHERE name IN ('Priya', 'Tis Customer')
AND pending_amount <= 0;


SELECT sale_id, name, gross_sales, received_amount, pending_amount, status
FROM customer_sales
WHERE name IN ('Priya', 'Test_Customer');

SELECT sale_id, name FROM customer_sales;

UPDATE customer_sales
SET status = 'Close'
WHERE sale_id IN (2, 3)
AND pending_amount <= 0;

SELECT * FROM customer_sales;


DROP TRIGGER IF EXISTS after_payment_insert;
SELECT 1;

SHOW CREATE TRIGGER after_payment_insert;

SELECT DATABASE();


DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_splits
        WHERE sale_id = NEW.sale_id
    ),
    status = CASE
        WHEN pending_amount <= 0 THEN 'Close'
        ELSE 'Open'
    END
    WHERE sale_id = NEW.sale_id;
END//

DELIMITER ;

SHOW TRIGGERS;


DROP TRIGGER IF EXISTS after_payment_insert;


show columns from payment_splits;

DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = received_amount + NEW.amount_paid
    WHERE sale_id = NEW.sale_id;
END//

DELIMITER ;

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
UPDATE customer_sales
SET status = IF(received_amount + NEW.amount_paid >= gross_sales, 'Close', 'Open'),
    received_amount = received_amount + NEW.amount_paid
WHERE sale_id = NEW.sale_id;


SHOW TRIGGERS LIKE 'payment_splits';


USE sales_intelligence_hub;
SELECT COUNT(*) AS user_count
FROM users;


USE sales_intelligence_hub;
SELECT user_id, username, branch_id, role, email
FROM users;

USE sales_intelligence_hub;
SELECT * FROM branches;

USE sales_intelligence_hub;

USE sales_intelligence_hub;
SELECT COUNT(*) FROM customer_sales;

USE sales_intelligence_hub;
SELECT * FROM customer_sales;


USE sales_intelligence_hub;
SELECT sale_id, branch_id, sale_date, name, product_name,
       gross_sales, received_amount, pending_amount, status
FROM customer_sales;


USE sales_intelligence_hub;
SELECT COUNT(*) AS total_reords FROM customer_sales;

USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;
DELETE FROM payment_splits;

USE sales_intelligence_hub;
SELECT COUNT(*) AS payment_records FROM payment_splits;


USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;

DELETE FROM customer_sales;

SELECT COUNT(*) AS total_sales
FROM customer_sales;

SET SQL_SAFE_UPDATES = 1;

USE sales_intelligence_hub;
SELECT COUNT(*) AS total_sales
FROM customer_sales;


USE sales_intelligence_hub;
SELECT COUNT(*) AS total_payments
FROM payment_splits;

USE sales_intelligence_hub;
SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM customer_sales
LIMIT 10;


USE sales_intelligence_hub;
SELECT 
    sale_id,
    gross_sales,
    received_amount,
    pending_amount,
    status
FROM customer_sales
WHERE received_amount = gross_sales
LIMIT 10;


USE sales_intelligence_hub;
SELECT
    cs.sale_id,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    COALESCE(SUM(ps.amount_paid), 0) AS actual_paid
FROM customer_sales cs
LEFT JOIN payment_splits ps
    ON cs.sale_id = ps.sale_id
GROUP BY
    cs.sale_id,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount
LIMIT 10;




USE sales_intelligence_hub;
SELECT
    cs.sale_id,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    COALESCE(SUM(ps.amount_paid), 0) AS actual_paid
FROM customer_sales cs
LEFT JOIN payment_splits ps
    ON cs.sale_id = ps.sale_id
GROUP BY
    cs.sale_id,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount
LIMIT 10;



USE sales_intelligence_hub;
SELECT
    cs.sale_id,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    cs.status
FROM customer_sales cs
WHERE cs.received_amount >= cs.gross_sales
LIMIT 10;


USE sales_intelligence_hub;
SELECT status, COUNT(*) AS total
FROM customer_sales
GROUP BY status;


USE sales_intelligence_hub;
SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM customer_sales
WHERE sale_id = 1;

USE sales_intelligence_hub;
SELECT * FROM users WHERE role = 'Super Admin';
SET SQL_SAFE_UPDATES = 0;

UPDATE users
SET password = 'super123'
WHERE username = 'superadmin';

SET SQL_SAFE_UPDATES = 1;

USE sales_intelligence_hub;
SELECT username , role FROM users WHERE username = 'superadmin';


USE sales_intelligence_hub;
SELECT username, role, branch_id
FROM users
WHERE role = 'Branch Admin';


USE sales_intelligence_hub;
SELECT username, role, branch_id
FROM users
ORDER BY role, username;

USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;

UPDATE users
SET username = 'admin_chennai'
WHERE username = 'chennaiadmin';

SET SQL_SAFE_UPDATES = 1;

USE sales_intelligence_hub;
SELECT username, role, branch_id
FROM users
WHERE username = 'admin_chennai';


USE sales_intelligence_hub;
SELECT
    u.username,
    u.role,
    u.branch_id,
    b.branch_name
FROM users u
LEFT JOIN branches b
    ON u.branch_id = b.branch_id
ORDER BY u.username;


USE sales_intelligence_hub;
SELECT branch_id, branch_name
FROM branches
ORDER BY branch_id;

USE sales_intelligence_hub;
SELECT branch_id, branch_name
FROM branches
ORDER BY branch_id;

USE sales_intelligence_hub;
SELECT branch_id, COUNT(*) AS sales_count
FROM customer_sales
GROUP BY branch_id
ORDER BY branch_id;

USE sales_intelligence_hub;
SELECT branch_id, branch_name, COUNT(*) AS sales_count
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY branch_id, branch_name
ORDER BY branch_id;


USE sales_intelligence_hub;
SELECT 
    cs.branch_id,
    b.branch_name,
    COUNT(*) AS sales_count
FROM customer_sales cs
JOIN branches b 
    ON cs.branch_id = b.branch_id
GROUP BY cs.branch_id, b.branch_name
ORDER BY cs.branch_id;

USE sales_intelligence_hub;
SELECT *
FROM branches
ORDER BY branch_id;


USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;

UPDATE users
SET branch_id = CASE username
    WHEN 'admin_ahmedabad' THEN 8
    WHEN 'admin_bangalore' THEN 4
    WHEN 'admin_chennai' THEN 1
    WHEN 'admin_delhi' THEN 2
    WHEN 'admin_kolkata' THEN 7
    WHEN 'admin_mumbai' THEN 3
    WHEN 'admin_pune' THEN 6
END
WHERE username IN (
    'admin_ahmedabad',
    'admin_bangalore',
    'admin_chennai',
    'admin_delhi',
    'admin_kolkata',
    'admin_mumbai',
    'admin_pune'
);

SET SQL_SAFE_UPDATES = 1;


USE sales_intelligence_hub;
SELECT username, role, branch_id
FROM users
ORDER BY username;

USE sales_intelligence_hub;
SELECT 
    u.username,
    u.role,
    u.branch_id,
    b.branch_name
FROM users u
LEFT JOIN branches b
    ON u.branch_id = b.branch_id
ORDER BY u.username;


USE sales_intelligence_hub;
SELECT * FROM branches WHERE branch_id IN (3 , 5);


USE sales_intelligence_hub;
SELECT username, role, branch_id
FROM users
WHERE username IN ('admin_hyderabad', 'admin_mumbai');


USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;

UPDATE users
SET branch_id = 5
WHERE username = 'admin_hyderabad';

UPDATE users
SET branch_id = 3
WHERE username = 'admin_mumbai';

SET SQL_SAFE_UPDATES = 1;

USE sales_intelligence_hub;
SELECT 
    u.username,
    u.branch_id,
    b.branch_name
FROM users u
LEFT JOIN branches b
    ON u.branch_id = b.branch_id
WHERE u.username IN ('admin_hyderabad', 'admin_mumbai');

USE sales_intelligence_hub;
SET SQL_SAFE_UPDATES = 0;

UPDATE branches
SET branch_name = 'Hyderabad'
WHERE branch_id = 5;

SET SQL_SAFE_UPDATES = 1;

USE sales_intelligence_hub;
SELECT branch_id, branch_name
FROM branches
ORDER BY branch_id;


USE sales_intelligence_hub;
DESCRIBE customer_sales;