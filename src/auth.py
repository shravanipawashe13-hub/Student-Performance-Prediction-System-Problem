"""
Authentication & Role-Based Access Control (RBAC) Module
Supports:
1. Admin (Full access + Teacher Account Management)
2. Teacher (Evaluation, Data Management, Reminders, Reports)
3. Student (View Personal Academic Report & Trajectory)
"""

import hashlib
import src.db as db

def hash_password(password: str) -> str:
    """Computes SHA-256 hash for secure credential storage."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def init_auth_table():
    """Creates the users table and seeds default accounts if empty."""
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    
    if engine == "SQLite":
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin', 'teacher', 'student'
            full_name TEXT NOT NULL,
            student_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:  # MySQL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            role VARCHAR(20) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            student_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    conn.commit()

    # Check if default accounts exist
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0] if engine == "SQLite" else list(cursor.fetchone().values())[0]
    
    if count == 0:
        default_users = [
            ("admin", hash_password("admin123"), "admin", "System Administrator", None),
            ("teacher", hash_password("teacher123"), "teacher", "Prof. Rajesh Gupta (BCA Faculty)", None),
            ("student", hash_password("student123"), "student", "Aarav Sharma", "STU1042")
        ]
        placeholder = "?" if engine == "SQLite" else "%s"
        query = f"INSERT INTO users (username, password_hash, role, full_name, student_id) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        cursor.executemany(query, default_users)
        conn.commit()

    conn.close()


def authenticate_user(username: str, password: str):
    """
    Authenticates a user by username and password.
    Returns user dict or None if invalid.
    """
    init_auth_table()
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    placeholder = "?" if engine == "SQLite" else "%s"
    
    cursor.execute(
        f"SELECT username, role, full_name, student_id FROM users WHERE LOWER(username) = LOWER({placeholder}) AND password_hash = {placeholder}",
        (username.strip(), pwd_hash)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if engine == "SQLite":
            return {
                "username": row["username"],
                "role": row["role"],
                "full_name": row["full_name"],
                "student_id": row["student_id"]
            }
        else:
            return {
                "username": row.get("username"),
                "role": row.get("role"),
                "full_name": row.get("full_name"),
                "student_id": row.get("student_id")
            }
    return None


def create_user(username: str, password: str, role: str, full_name: str, student_id: str = None):
    """Creates a new user account (e.g. Admin creating a Teacher)."""
    init_auth_table()
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    placeholder = "?" if engine == "SQLite" else "%s"
    
    # Check if username exists
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE LOWER(username) = LOWER({placeholder})", (username.strip(),))
    exists = cursor.fetchone()[0] if engine == "SQLite" else list(cursor.fetchone().values())[0]
    if exists > 0:
        conn.close()
        return False, f"Username '{username}' already exists. Please choose a different username."

    pwd_hash = hash_password(password)
    query = f"INSERT INTO users (username, password_hash, role, full_name, student_id) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
    cursor.execute(query, (username.strip(), pwd_hash, role, full_name.strip(), student_id))
    conn.commit()
    conn.close()
    return True, f"Account '{username}' ({role.capitalize()}) successfully created!"


def get_all_users():
    """Retrieves all registered users for Admin inspection."""
    init_auth_table()
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name, student_id, created_at FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for r in rows:
        if engine == "SQLite":
            users.append(dict(r))
        else:
            users.append(r)
    return users


def delete_user(username: str):
    """Deletes a user account."""
    if username.lower() == "admin":
        return False, "Cannot delete the primary root admin account."
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    placeholder = "?" if engine == "SQLite" else "%s"
    cursor.execute(f"DELETE FROM users WHERE LOWER(username) = LOWER({placeholder})", (username.strip(),))
    conn.commit()
    conn.close()
    return True, f"User '{username}' deleted successfully."


def auto_create_student_account(student_id: str, student_name: str, password: str = "student123"):
    """
    Automatically creates a student login account when a new student record is added.
    Username: student_id.lower()
    Password: default 'student123'
    """
    init_auth_table()
    username = student_id.strip().lower()
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    placeholder = "?" if engine == "SQLite" else "%s"
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE LOWER(username) = LOWER({placeholder})", (username,))
    count = cursor.fetchone()[0] if engine == "SQLite" else list(cursor.fetchone().values())[0]
    conn.close()
    
    if count == 0:
        create_user(username, password, "student", student_name.strip(), student_id.strip())
        return True, username
    return False, username


def get_student_users():
    """Retrieves all registered student accounts."""
    init_auth_table()
    conn, engine = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, full_name, student_id FROM users WHERE role = 'student' ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    students = []
    for r in rows:
        students.append(dict(r) if hasattr(r, "keys") else {"username": r[0], "full_name": r[1], "student_id": r[2]})
    return students


def sync_students_with_users():
    """Ensures every student present in SQL database has a corresponding student login account."""
    init_auth_table()
    try:
        students_df = db.fetch_all_student_records()
        for _, row in students_df.iterrows():
            sid = str(row["Student_ID"]).strip()
            sname = str(row["Student_Name"]).strip()
            auto_create_student_account(sid, sname, "student123")
    except Exception:
        pass

