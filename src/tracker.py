"""
Tracker & Persistence Module
Synchronizes with SQL Database (SQLite / MySQL) and local CSV caches.
"""

import os
import json
import datetime
import pandas as pd
import numpy as np
import src.db as db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "student_history.csv")
PERIODIC_FILE = os.path.join(DATA_DIR, "periodic_evaluations.csv")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")


def init_tracker_data():
    """Initializes SQL database and local cache files."""
    os.makedirs(DATA_DIR, exist_ok=True)
    db.init_database()
    
    # Ensure periodic file exists
    if not os.path.exists(PERIODIC_FILE):
        seed_periodic = [
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Monthly", "Period": "Month 1 (Apr)", "Attendance": 80.0, "Study_Hours": 14.0, "Internal_Score": 36.0, "Predicted_Score": 72.0, "Tier": "Merit"},
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Monthly", "Period": "Month 2 (May)", "Attendance": 82.0, "Study_Hours": 16.0, "Internal_Score": 38.0, "Predicted_Score": 74.5, "Tier": "Merit"},
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Monthly", "Period": "Month 3 (Jun)", "Attendance": 85.0, "Study_Hours": 17.5, "Internal_Score": 40.0, "Predicted_Score": 77.0, "Tier": "Merit"},
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Monthly", "Period": "Month 4 (Jul)", "Attendance": 88.0, "Study_Hours": 18.5, "Internal_Score": 42.0, "Predicted_Score": 79.4, "Tier": "Merit"},
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Quarterly", "Period": "Q1 (Foundations)", "Attendance": 81.0, "Study_Hours": 15.0, "Internal_Score": 37.0, "Predicted_Score": 73.2, "Tier": "Merit"},
            {"Student_ID": "STU1042", "Student_Name": "Aarav Sharma", "Cycle_Type": "Quarterly", "Period": "Q2 (Mid-Term)", "Attendance": 87.0, "Study_Hours": 18.0, "Internal_Score": 41.5, "Predicted_Score": 78.5, "Tier": "Merit"},
            
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Monthly", "Period": "Month 1 (Apr)", "Attendance": 75.0, "Study_Hours": 11.0, "Internal_Score": 30.0, "Predicted_Score": 58.0, "Tier": "Pass"},
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Monthly", "Period": "Month 2 (May)", "Attendance": 68.0, "Study_Hours": 9.0, "Internal_Score": 26.0, "Predicted_Score": 51.5, "Tier": "Pass"},
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Monthly", "Period": "Month 3 (Jun)", "Attendance": 62.0, "Study_Hours": 7.5, "Internal_Score": 24.0, "Predicted_Score": 46.8, "Tier": "At-Risk"},
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Monthly", "Period": "Month 4 (Jul)", "Attendance": 58.0, "Study_Hours": 6.0, "Internal_Score": 21.0, "Predicted_Score": 43.1, "Tier": "At-Risk"},
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Quarterly", "Period": "Q1 (Foundations)", "Attendance": 72.0, "Study_Hours": 10.0, "Internal_Score": 28.5, "Predicted_Score": 55.0, "Tier": "Pass"},
            {"Student_ID": "STU1105", "Student_Name": "Rohan Verma", "Cycle_Type": "Quarterly", "Period": "Q2 (Mid-Term)", "Attendance": 60.0, "Study_Hours": 6.8, "Internal_Score": 22.5, "Predicted_Score": 45.0, "Tier": "At-Risk"},
            
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Monthly", "Period": "Month 1 (Apr)", "Attendance": 90.0, "Study_Hours": 20.0, "Internal_Score": 44.0, "Predicted_Score": 86.0, "Tier": "Distinction"},
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Monthly", "Period": "Month 2 (May)", "Attendance": 92.0, "Study_Hours": 22.0, "Internal_Score": 45.5, "Predicted_Score": 88.5, "Tier": "Distinction"},
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Monthly", "Period": "Month 3 (Jun)", "Attendance": 93.0, "Study_Hours": 23.0, "Internal_Score": 46.0, "Predicted_Score": 89.8, "Tier": "Distinction"},
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Monthly", "Period": "Month 4 (Jul)", "Attendance": 94.0, "Study_Hours": 24.0, "Internal_Score": 47.0, "Predicted_Score": 91.2, "Tier": "Distinction"},
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Quarterly", "Period": "Q1 (Foundations)", "Attendance": 91.0, "Study_Hours": 21.0, "Internal_Score": 44.5, "Predicted_Score": 87.2, "Tier": "Distinction"},
            {"Student_ID": "STU1088", "Student_Name": "Priya Patel", "Cycle_Type": "Quarterly", "Period": "Q2 (Mid-Term)", "Attendance": 93.5, "Study_Hours": 23.5, "Internal_Score": 46.5, "Predicted_Score": 90.5, "Tier": "Distinction"}
        ]
        pd.DataFrame(seed_periodic).to_csv(PERIODIC_FILE, index=False)

    # Ensure reminders file exists
    if not os.path.exists(REMINDERS_FILE):
        seed_reminders = [
            {
                "id": "REM-101",
                "title": "Critical Attendance Alert: Rohan Verma",
                "student_id": "STU1105",
                "student_name": "Rohan Verma",
                "type": "Attendance Deficit",
                "frequency": "Immediate / Weekly",
                "due_date": "2026-09-18",
                "priority": "High",
                "status": "Pending",
                "message": "Attendance dropped to 58.0% (below 75% cutoff). Schedule mandatory parent counseling."
            },
            {
                "id": "REM-102",
                "title": "Quarterly Evaluation Q3 Reminder",
                "student_id": "ALL",
                "student_name": "All BCA Students (Cohort 2026)",
                "type": "Periodic Review",
                "frequency": "Quarterly",
                "due_date": "2026-09-30",
                "priority": "Medium",
                "status": "Pending",
                "message": "Mid-term internal exam marks submission and Q3 Performance Model evaluation."
            },
            {
                "id": "REM-103",
                "title": "Monthly Progress Review - September",
                "student_id": "ALL",
                "student_name": "BCA 5th Semester Students",
                "type": "Periodic Review",
                "frequency": "Monthly",
                "due_date": "2026-09-25",
                "priority": "Medium",
                "status": "Pending",
                "message": "Run monthly performance predictions for students with internal scores < 25."
            },
            {
                "id": "REM-104",
                "title": "Remedial Coding Classes for At-Risk Students",
                "student_id": "STU1105",
                "student_name": "Rohan Verma",
                "type": "Academic Remediation",
                "frequency": "Bi-Weekly",
                "due_date": "2026-09-22",
                "priority": "High",
                "status": "In Progress",
                "message": "Assign student mentor for Data Structures and C++ fundamentals lab."
            }
        ]
        with open(REMINDERS_FILE, "w") as f:
            json.dump(seed_reminders, f, indent=4)


def get_evaluation_history() -> pd.DataFrame:
    """Fetches evaluation history directly from SQL Database."""
    return db.fetch_all_student_records()


def add_evaluation_record(record: dict):
    """Inserts record into SQL Database and syncs CSV."""
    db.insert_student_record(record)
    df = db.fetch_all_student_records()
    df.to_csv(HISTORY_FILE, index=False)
    return df


def delete_evaluation_record(eval_id: str):
    """Deletes record from SQL database."""
    db.delete_student_record(eval_id)
    df = db.fetch_all_student_records()
    df.to_csv(HISTORY_FILE, index=False)
    return df


def get_periodic_evaluations() -> pd.DataFrame:
    init_tracker_data()
    return pd.read_csv(PERIODIC_FILE)


def add_periodic_evaluation(record: dict):
    init_tracker_data()
    df = pd.read_csv(PERIODIC_FILE)
    new_df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    new_df.to_csv(PERIODIC_FILE, index=False)
    return new_df


def get_reminders() -> list:
    init_tracker_data()
    try:
        with open(REMINDERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_reminders(reminders: list):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=4)


def add_reminder(reminder: dict):
    reminders = get_reminders()
    reminders.insert(0, reminder)
    save_reminders(reminders)
    return reminders


def update_reminder_status(rem_id: str, new_status: str):
    reminders = get_reminders()
    for rem in reminders:
        if rem["id"] == rem_id:
            rem["status"] = new_status
            break
    save_reminders(reminders)
    return reminders


def delete_reminder(rem_id: str):
    reminders = get_reminders()
    reminders = [r for r in reminders if r["id"] != rem_id]
    save_reminders(reminders)
    return reminders
