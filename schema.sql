-- Database Initialization Script
-- Project: Intelligent Battery RUL Prediction System
-- Target DBMS: MySQL 8.0+

CREATE DATABASE IF NOT EXISTS `battery_rul_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `battery_rul_db`;

-- Table 1: System Users & Roles
CREATE TABLE IF NOT EXISTS `users` (
    `user_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'engineer', 'viewer') NOT NULL DEFAULT 'engineer',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: Battery Metadata Specifications
CREATE TABLE IF NOT EXISTS `battery_metadata` (
    `battery_id` VARCHAR(64) PRIMARY KEY,
    `chemistry_type` ENUM('NMC', 'LFP', 'LCO', 'NCA', 'LTO') NOT NULL,
    `nominal_capacity_ah` DECIMAL(8,4) NOT NULL,
    `rated_voltage_v` DECIMAL(6,3) NOT NULL,
    `temp_limit_min_c` DECIMAL(5,2) DEFAULT -20.00,
    `temp_limit_max_c` DECIMAL(5,2) DEFAULT 60.00,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_chemistry` (`chemistry_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3: Lifecycle Operational Metrics
CREATE TABLE IF NOT EXISTS `cycle_data` (
    `record_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `battery_id` VARCHAR(64) NOT NULL,
    `cycle_number` INT UNSIGNED NOT NULL,
    `voltage_measured_v` DECIMAL(8,4) NOT NULL,
    `current_measured_a` DECIMAL(8,4) NOT NULL,
    `temperature_measured_c` DECIMAL(6,2) NOT NULL,
    `capacity_ah` DECIMAL(8,4) NOT NULL,
    `soh_percent` DECIMAL(5,2) GENERATED ALWAYS AS (
        (`capacity_ah` / NULLIF((SELECT `nominal_capacity_ah` FROM `battery_metadata` WHERE `battery_metadata`.`battery_id` = `cycle_data`.`battery_id`), 0)) * 100
    ) STORED,
    `internal_resistance_ohm` DECIMAL(10,6) NOT NULL,
    `recorded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_cycle_battery` FOREIGN KEY (`battery_id`) 
        REFERENCES `battery_metadata` (`battery_id`) ON DELETE CASCADE,
    CONSTRAINT `unique_battery_cycle` UNIQUE (`battery_id`, `cycle_number`),
    INDEX `idx_battery_cycle` (`battery_id`, `cycle_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 4: MLP Model Inference Outputs & RUL Predictions
CREATE TABLE IF NOT EXISTS `rul_predictions` (
    `prediction_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `battery_id` VARCHAR(64) NOT NULL,
    `cycle_number` INT UNSIGNED NOT NULL,
    `predicted_rul_cycles` INT NOT NULL,
    `actual_rul_cycles` INT NULL,
    `error_metric_mae` DECIMAL(8,4) NULL,
    `prediction_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_prediction_battery` FOREIGN KEY (`battery_id`) 
        REFERENCES `battery_metadata` (`battery_id`) ON DELETE CASCADE,
    INDEX `idx_prediction_battery` (`battery_id`),
    INDEX `idx_timestamp` (`prediction_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;