-- Gold Jewellery Pledge and Interest Calculation System
-- Run this script in MySQL to create the database and tables

CREATE DATABASE IF NOT EXISTS gold_pledge_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gold_pledge_db;

CREATE TABLE IF NOT EXISTS pledges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_address TEXT,
    jewellery_type VARCHAR(100) NOT NULL,
    jewellery_weight DECIMAL(10, 3) NOT NULL COMMENT 'Weight in grams',
    jewellery_purity VARCHAR(50) DEFAULT NULL COMMENT 'e.g. 22K, 24K',
    jewellery_description TEXT,
    loan_amount DECIMAL(12, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) NOT NULL COMMENT 'Annual interest percentage',
    pledge_date DATE NOT NULL,
    return_date DATE NOT NULL,
    total_days INT NOT NULL,
    per_day_interest DECIMAL(12, 4) NOT NULL,
    total_interest DECIMAL(12, 2) NOT NULL,
    final_amount DECIMAL(12, 2) NOT NULL,
    status ENUM('active', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_phone (customer_phone),
    INDEX idx_pledge_date (pledge_date),
    INDEX idx_status (status)
) ENGINE=InnoDB;
