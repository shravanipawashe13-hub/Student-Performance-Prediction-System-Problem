"""
SQL Database Manager for Student Performance Prediction System
Supports both SQLite (built-in zero-config SQL engine) and MySQL.
"""

import os
import sqlite3
import pandas as pd
import datetime

# Try importing pymysql for MySQL connectivity
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "student_records.db")

# Default connection mode: SQLite (auto-created in data/student_records.db)
# Can be switched to MySQL dynamically via UI or set_mysql_config
_MYSQL_CONFIG = None


def get_connection():
    """
    Returns an active database connection:
    - MySQL if configured and reachable
    - SQLite (default zero-config file database)
    """
    global _MYSQL_CONFIG
    if _MYSQL_CONFIG and PYMYSQL_AVAILABLE:
        try:
            conn = pymysql.connect(
                host=_MYSQL_CONFIG.get("host", "localhost"),
                user=_MYSQL_CONFIG.get("user", "root"),
                password=_MYSQL_CONFIG.get("password", ""),
                database=_MYSQL_CONFIG.get("database", "student_performance_db"),
                port=int(_MYSQL_CONFIG.get("port", 3306)),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn, "MySQL"
        except Exception:
            pass  # Fall back to SQLite gracefully

    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "SQLite"


def init_database():
    """Initializes tables and seeds baseline records if empty."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    
    if engine == "SQLite":
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_evaluations (
            Evaluation_ID TEXT PRIMARY KEY,
            Evaluation_Date TEXT,
            Student_ID TEXT,
            Student_Name TEXT,
            Attendance_Rate REAL,
            Study_Hours_Per_Week REAL,
            Internal_Assessment_Score REAL,
            Past_Exam_Score REAL,
            Sleep_Hours_Per_Day REAL,
            Predicted_Score REAL,
            Performance_Category TEXT,
            Status TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS periodic_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID TEXT,
            Student_Name TEXT,
            Cycle_Type TEXT,
            Period TEXT,
            Attendance REAL,
            Study_Hours REAL,
            Internal_Score REAL,
            Predicted_Score REAL,
            Tier TEXT
        )
        """)
    else:  # MySQL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_evaluations (
            Evaluation_ID VARCHAR(50) PRIMARY KEY,
            Evaluation_Date VARCHAR(20),
            Student_ID VARCHAR(50),
            Student_Name VARCHAR(100),
            Attendance_Rate FLOAT,
            Study_Hours_Per_Week FLOAT,
            Internal_Assessment_Score FLOAT,
            Past_Exam_Score FLOAT,
            Sleep_Hours_Per_Day FLOAT,
            Predicted_Score FLOAT,
            Performance_Category VARCHAR(50),
            Status VARCHAR(50)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS periodic_evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Student_ID VARCHAR(50),
            Student_Name VARCHAR(100),
            Cycle_Type VARCHAR(20),
            Period VARCHAR(50),
            Attendance FLOAT,
            Study_Hours FLOAT,
            Internal_Score FLOAT,
            Predicted_Score FLOAT,
            Tier VARCHAR(50)
        )
        """)

    conn.commit()
    
    # Check if baseline data exists, if not seed from CSV or defaults
    cursor.execute("SELECT COUNT(*) FROM student_evaluations")
    count = cursor.fetchone()[0] if engine == "SQLite" else list(cursor.fetchone().values())[0]
    
    if count == 0:
        seed_students = [
            ("EV-1001", "2026-08-10", "STU1042", "Aarav Sharma", 88.0, 18.5, 42.0, 76.0, 7.5, 79.4, "Merit", "On Track"),
            ("EV-1002", "2026-08-15", "STU1088", "Priya Patel", 94.0, 24.0, 47.0, 89.0, 8.0, 91.2, "Distinction", "High Achiever"),
            ("EV-1003", "2026-08-20", "STU1105", "Rohan Verma", 58.0, 6.0, 21.0, 44.0, 5.0, 43.1, "At-Risk", "Critical Warning"),
            ("EV-1004", "2026-08-28", "STU1140", "Ananya Iyer", 74.0, 12.0, 31.0, 62.0, 7.0, 63.8, "Pass", "Attendance Alert"),
            ("EV-1005", "2026-09-02", "STU1192", "Vikram Malhotra", 82.0, 15.0, 36.0, 71.0, 7.5, 72.5, "Merit", "On Track")
        ]
        
        placeholder = "?" if engine == "SQLite" else "%s"
        insert_query = f"""
        INSERT INTO student_evaluations (
            Evaluation_ID, Evaluation_Date, Student_ID, Student_Name,
            Attendance_Rate, Study_Hours_Per_Week, Internal_Assessment_Score,
            Past_Exam_Score, Sleep_Hours_Per_Day, Predicted_Score,
            Performance_Category, Status
        ) VALUES ({','.join([placeholder]*12)})
        """
        cursor.executemany(insert_query, seed_students)
        conn.commit()

    conn.close()


def insert_student_record(record: dict) -> bool:
    """Inserts a new student evaluation into the SQL database."""
    init_database()
    conn, engine = get_connection()
    cursor = conn.cursor()
    
    placeholder = "?" if engine == "SQLite" else "%s"
    fields = [
        "Evaluation_ID", "Evaluation_Date", "Student_ID", "Student_Name",
        "Attendance_Rate", "Study_Hours_Per_Week", "Internal_Assessment_Score",
        "Past_Exam_Score", "Sleep_Hours_Per_Day", "Predicted_Score",
        "Performance_Category", "Status"
    ]
    
    vals = [
        record.get("Evaluation_ID", f"EV-{datetime.datetime.now().strftime('%M%S')}"),
        record.get("Evaluation_Date", datetime.date.today().strftime("%Y-%m-%d")),
        record.get("Student_ID", "STU9999"),
        record.get("Student_Name", "New Student"),
        float(record.get("Attendance_Rate", 75.0)),
        float(record.get("Study_Hours_Per_Week", 12.0)),
        float(record.get("Internal_Assessment_Score", 30.0)),
        float(record.get("Past_Exam_Score", 60.0)),
        float(record.get("Sleep_Hours_Per_Day", 7.0)),
        float(record.get("Predicted_Score", 65.0)),
        record.get("Performance_Category", "Pass"),
        record.get("Status", "On Track")
    ]
    
    query = f"INSERT OR REPLACE INTO student_evaluations ({','.join(fields)}) VALUES ({','.join([placeholder]*len(fields))})" if engine == "SQLite" else f"REPLACE INTO student_evaluations ({','.join(fields)}) VALUES ({','.join([placeholder]*len(fields))})"
    
    cursor.execute(query, vals)
    conn.commit()
    conn.close()
    return True


def fetch_all_student_records() -> pd.DataFrame:
    """Fetches all evaluations from the SQL database."""
    init_database()
    conn, engine = get_connection()
    df = pd.read_sql_query("SELECT * FROM student_evaluations ORDER BY Evaluation_Date DESC, Evaluation_ID DESC", conn)
    conn.close()
    return df


def delete_student_record(eval_id: str) -> bool:
    """Deletes an evaluation by ID."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    placeholder = "?" if engine == "SQLite" else "%s"
    cursor.execute(f"DELETE FROM student_evaluations WHERE Evaluation_ID = {placeholder}", (eval_id,))
    conn.commit()
    conn.close()
    return True


def clear_all_student_records() -> bool:
    """Clears all student records from the SQL database."""
    conn, engine = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_evaluations")
    conn.commit()
    conn.close()
    return True


def check_student_exists(student_id: str):
    """
    Checks if a student with this Student_ID already exists.
    Returns (exists: bool, student_name: str, evaluation_date: str)
    """
    init_database()
    conn, engine = get_connection()
    cursor = conn.cursor()
    placeholder = "?" if engine == "SQLite" else "%s"
    cursor.execute(f"SELECT Student_ID, Student_Name, Evaluation_Date FROM student_evaluations WHERE UPPER(Student_ID) = UPPER({placeholder})", (student_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        if engine == "SQLite":
            return True, row["Student_Name"], row["Evaluation_Date"]
        else:
            return True, row.get("Student_Name"), row.get("Evaluation_Date")
    return False, None, None


def get_current_sql_engine():
    """Returns database type and info."""
    conn, engine = get_connection()
    conn.close()
    if engine == "SQLite":
        return "SQLite SQL Database", SQLITE_DB_PATH
    else:
        return "MySQL Database", f"{_MYSQL_CONFIG.get('host', 'localhost')}:{_MYSQL_CONFIG.get('port', 3306)}"


def configure_mysql(host="localhost", user="root", password="", database="student_performance_db", port=3306):
    """Configures MySQL credentials and attempts connection."""
    global _MYSQL_CONFIG
    if not PYMYSQL_AVAILABLE:
        return False, "PyMySQL library is not installed."
    try:
        # First connect without database to create if not exists
        temp_conn = pymysql.connect(
            host=host, user=user, password=password, port=int(port), autocommit=True
        )
        temp_cur = temp_conn.cursor()
        temp_cur.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        temp_conn.close()
        
        _MYSQL_CONFIG = {
            "host": host, "user": user, "password": password,
            "database": database, "port": port
        }
        init_database()
        return True, f"Successfully connected to MySQL database '{database}'!"
    except Exception as e:
        return False, f"Failed to connect to MySQL: {e}"
