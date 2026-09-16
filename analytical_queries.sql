CREATE DATABASE sales_intelligence_hub;
USE sales_intelligence_hub;
CREATE TABLE branches (
	branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
	branch_admin_name VARCHAR(100) NOT NULL
);



CREATE TABLE customer_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    sale_date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    product_name VARCHAR(30) NOT NULL,
    gross_sales DECIMAL(12,2) NOT NULL,
    received_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    pending_amount DECIMAL(12,2)
        GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status ENUM('Open', 'Close') NOT NULL DEFAULT 'Open',

    CONSTRAINT fk_sales_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


CREATE TABLE payment_splits (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,

    CONSTRAINT fk_payment_sale
        FOREIGN KEY (sale_id)
        REFERENCES customer_sales(sale_id)
);


CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    branch_id INT,
    role ENUM('Super Admin', 'Admin') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,

    CONSTRAINT fk_user_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


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
    )
    WHERE sale_id = NEW.sale_id;

END //

DELIMITER ;


INSERT INTO branches
(branch_name, branch_admin_name)
VALUES
('Chennai', 'Arun'),
('Delhi', 'Rahul'),
('Mumbai', 'Priya'),
('Bangalore', 'Kiran');


SELECT SUM(gross_sales) AS total_gross_sales
FROM customer_sales;

SELECT SUM(received_amount) AS total_received
FROM customer_sales;

SELECT SUM(pending_amount) AS total_pending
FROM customer_sales;


SELECT
    b.branch_name,
    COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs
    ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name;

SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_sales
FROM branches b
JOIN customer_sales cs
    ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name;


SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;


USE sales_intelligence_hub;
SELECT*FROM branches;