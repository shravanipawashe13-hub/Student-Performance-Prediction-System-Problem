-- =============================================================================
-- MySQL Database Setup Script for Student Performance Prediction System
-- BCA Final Year Project
-- =============================================================================

CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

-- 1. Table for Student Historical Evaluations
CREATE TABLE IF NOT EXISTS student_evaluations (
    Evaluation_ID VARCHAR(50) PRIMARY KEY,
    Evaluation_Date DATE,
    Student_ID VARCHAR(50) NOT NULL,
    Student_Name VARCHAR(100) NOT NULL,
    Attendance_Rate FLOAT NOT NULL,
    Study_Hours_Per_Week FLOAT NOT NULL,
    Internal_Assessment_Score FLOAT NOT NULL,
    Past_Exam_Score FLOAT NOT NULL,
    Sleep_Hours_Per_Day FLOAT NOT NULL,
    Predicted_Score FLOAT NOT NULL,
    Performance_Category VARCHAR(50) NOT NULL,
    Status VARCHAR(50) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table for Periodic Evaluations (Monthly / Quarterly)
CREATE TABLE IF NOT EXISTS periodic_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID VARCHAR(50) NOT NULL,
    Student_Name VARCHAR(100) NOT NULL,
    Cycle_Type VARCHAR(20) NOT NULL,  -- 'Monthly' or 'Quarterly'
    Period VARCHAR(50) NOT NULL,      -- e.g. 'Month 1 (Apr)', 'Q1 (Foundations)'
    Attendance FLOAT NOT NULL,
    Study_Hours FLOAT NOT NULL,
    Internal_Score FLOAT NOT NULL,
    Predicted_Score FLOAT NOT NULL,
    Tier VARCHAR(50) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Seed Sample Records
INSERT INTO student_evaluations (
    Evaluation_ID, Evaluation_Date, Student_ID, Student_Name,
    Attendance_Rate, Study_Hours_Per_Week, Internal_Assessment_Score,
    Past_Exam_Score, Sleep_Hours_Per_Day, Predicted_Score,
    Performance_Category, Status
) VALUES
('EV-1001', '2026-08-10', 'STU1042', 'Aarav Sharma', 88.0, 18.5, 42.0, 76.0, 7.5, 79.4, 'Merit', 'On Track'),
('EV-1002', '2026-08-15', 'STU1088', 'Priya Patel', 94.0, 24.0, 47.0, 89.0, 8.0, 91.2, 'Distinction', 'High Achiever'),
('EV-1003', '2026-08-20', 'STU1105', 'Rohan Verma', 58.0, 6.0, 21.0, 44.0, 5.0, 43.1, 'At-Risk', 'Critical Warning'),
('EV-1004', '2026-08-28', 'STU1140', 'Ananya Iyer', 74.0, 12.0, 31.0, 62.0, 7.0, 63.8, 'Pass', 'Attendance Alert'),
('EV-1005', '2026-09-02', 'STU1192', 'Vikram Malhotra', 82.0, 15.0, 36.0, 71.0, 7.5, 72.5, 'Merit', 'On Track')
ON DUPLICATE KEY UPDATE Predicted_Score=VALUES(Predicted_Score);
