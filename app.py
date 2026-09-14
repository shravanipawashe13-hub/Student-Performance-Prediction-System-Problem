"""
Student Performance Prediction System
Interactive Web Application powered by Streamlit & Scikit-Learn Decision Trees
Role-Based Access Control (RBAC):
- Admin (Full system access + Teacher Account Management)
- Teacher (Live Predictor, Periodic Evaluations, SQL Database Management, Reminders, Report Cards)
- Student (Personalized Academic Report Card & Progress Trajectory)
"""

import sys
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_best_python():
    """
    Dynamically discovers the best available Python interpreter on ANY PC.
    Prioritizes Python 3.9 - 3.13 to ensure 100% compatibility with binary C-extensions.
    """
    # If currently running Python is within standard 3.8 - 3.13 range, use it directly
    if (3, 8) <= sys.version_info < (3, 14):
        return sys.executable

    # If on Python 3.14+ (or experimental build), search for a stable Python 3.10-3.13
    if sys.platform.startswith("win"):
        # 1. Try Windows py launcher
        for py_ver in ["-3.12", "-3.11", "-3.13", "-3.10", "-3"]:
            try:
                out = subprocess.check_output(["py", py_ver, "-c", "import sys; print(sys.executable)"], text=True, stderr=subprocess.DEVNULL).strip()
                if out and os.path.exists(out):
                    return out
            except Exception:
                pass

        # 2. Check dynamic AppData or ProgramFiles paths on Windows
        local_app = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        search_dirs = [
            os.path.join(local_app, "Programs", "Python"),
            prog_files,
            prog_files_x86,
            "C:\\"
        ]
        for sdir in search_dirs:
            if os.path.exists(sdir):
                for py_folder in ["Python312", "Python311", "Python313", "Python310"]:
                    candidate = os.path.join(sdir, py_folder, "python.exe")
                    if os.path.exists(candidate):
                        return candidate

    return sys.executable


def should_auto_launch() -> bool:
    """Returns True ONLY if app.py was executed directly with `python app.py` outside Streamlit."""
    # 1. If already launched by a runner or child process, do not re-launch
    if os.environ.get("STREAMLIT_AUTO_LAUNCHED") == "1":
        return False

    # 2. If executed via streamlit CLI (e.g. `streamlit run app.py`)
    for arg in sys.argv:
        if "streamlit" in os.path.basename(arg).lower():
            return False

    # 3. Check Streamlit runtime context
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            return False
    except Exception:
        pass

    # 4. Only auto-launch if directly executed as main script via python.exe
    return (__name__ == "__main__")


if should_auto_launch():
    target_py = find_best_python()
    print(f"Launching Student Performance Prediction System via: {target_py}")
    env = os.environ.copy()
    env["STREAMLIT_AUTO_LAUNCHED"] = "1"
    res = subprocess.run([target_py, "-m", "streamlit", "run", os.path.abspath(__file__)], env=env)
    sys.exit(res.returncode)

import json
import pickle
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import src.tracker as tracker
import src.db as db
import src.auth as auth

# Set page layout and title
st.set_page_config(
    page_title="Student Performance Prediction System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and modern typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        padding-bottom: 8px;
    }
    .main-header p {
        color: #e2e8f0;
        font-size: 1.05rem;
        margin: 0;
    }
    
    .login-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        max-width: 480px;
        margin: 0 auto;
    }
    
    .report-card-container {
        background: #ffffff;
        border: 2px solid #1e3c72;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        color: #1e293b;
        margin-bottom: 24px;
    }
    
    .report-header {
        text-align: center;
        border-bottom: 2px solid #1e3c72;
        padding-bottom: 16px;
        margin-bottom: 24px;
    }
    
    .badge-distinction {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    .badge-merit {
        background-color: #dcfce7;
        color: #15803d;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    .badge-pass {
        background-color: #fef9c3;
        color: #a16207;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    .badge-risk {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
    }
    
    .rec-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
    }

    .reminder-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .priority-high {
        border-left: 5px solid #ef4444;
    }
    .priority-medium {
        border-left: 5px solid #f59e0b;
    }
    .priority-low {
        border-left: 5px solid #10b981;
    }

    .report-card-container {
        background: #ffffff;
        border: 2px solid #1e3c72;
        border-radius: 12px;
        padding: 28px;
        color: #1e293b;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin: 15px 0 25px 0;
    }
    .report-header {
        text-align: center;
        border-bottom: 2px solid #1e3c72;
        padding-bottom: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_artifacts():
    """Loads trained models, encoders, and performance metadata. Auto-initializes if missing."""
    model_dir = os.path.join(BASE_DIR, "models")
    data_dir = os.path.join(BASE_DIR, "data")
    
    clf_path = os.path.join(model_dir, "decision_tree_classifier.pkl")
    data_file = os.path.join(data_dir, "student_performance_cleaned.csv")
    
    # Auto-generate dataset and train models if launching on a clean PC
    if not os.path.exists(clf_path) or not os.path.exists(data_file):
        try:
            import src.data_prep as dp
            import src.eda as eda
            import src.train as tr
            dp.save_all_datasets()
            eda.run_eda()
            tr.train_decision_tree_models()
        except Exception as bootstrap_err:
            print(f"Auto-bootstrap note: {bootstrap_err}")

    try:
        with open(os.path.join(model_dir, "decision_tree_classifier.pkl"), "rb") as f:
            clf = pickle.load(f)
        with open(os.path.join(model_dir, "decision_tree_regressor.pkl"), "rb") as f:
            reg = pickle.load(f)
        with open(os.path.join(model_dir, "encoders.pkl"), "rb") as f:
            encoders = pickle.load(f)
        with open(os.path.join(model_dir, "model_metadata.json"), "r") as f:
            meta = json.load(f)
        return clf, reg, encoders, meta, True
    except Exception as e:
        return None, None, None, None, False


clf, reg, encoders, meta, loaded = load_artifacts()

# Initialize DB & Auth & Sync all registered students as login users
auth.init_auth_table()
auth.sync_students_with_users()
tracker.init_tracker_data()


# =============================================================================
# 🔐 AUTHENTICATION & LOGIN SCREEN
# =============================================================================
if not st.session_state.get("authenticated", False):
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 24px;">
        <h1 style="color: #1e3c72; font-size: 2.4rem; font-weight: 800;">🎓 Student Performance Prediction System</h1>
        <p style="color: #64748b; font-size: 1.1rem;">BCA Final Year Academic Project • Role-Based Secure Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    l_col1, l_col2, l_col3 = st.columns([1, 1.2, 1])
    
    with l_col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("Sign In to Access Portal")
        
        login_user = st.text_input("Username / Student ID", placeholder="e.g., admin, teacher, or stu1042")
        login_pwd = st.text_input("Password", type="password", placeholder="Enter password (default: student123)")
        
        if st.button("🔐 Login to System", type="primary", use_container_width=True):
            user_data = auth.authenticate_user(login_user, login_pwd)
            if user_data:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user_data
                st.success(f"Welcome back, {user_data['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password. (For students, username is Student ID in lowercase e.g. 'stu1042', password 'student123')")
                
        st.divider()
        st.markdown("##### 🚀 Quick Demo Accounts (1-Click Login):")
        
        q_col1, q_col2, q_col3 = st.columns(3)
        with q_col1:
            if st.button("👑 Admin", use_container_width=True):
                user_data = auth.authenticate_user("admin", "admin123")
                st.session_state["authenticated"] = True
                st.session_state["user"] = user_data
                st.rerun()
        with q_col2:
            if st.button("👩‍🏫 Teacher", use_container_width=True):
                user_data = auth.authenticate_user("teacher", "teacher123")
                st.session_state["authenticated"] = True
                st.session_state["user"] = user_data
                st.rerun()
        with q_col3:
            if st.button("🎓 Student Demo", use_container_width=True):
                user_data = auth.authenticate_user("student", "student123")
                st.session_state["authenticated"] = True
                st.session_state["user"] = user_data
                st.rerun()

        # Dynamic Student Selector for Any Added Student
        student_users = auth.get_student_users()
        if student_users:
            st.markdown("---")
            st.markdown("##### 🎓 Or Login as Any Registered Student:")
            s_labels = [f"{s['full_name']} ({s['student_id']})" for s in student_users]
            picked_s = st.selectbox("Select Student Account:", s_labels, key="login_student_dropdown")
            if st.button("🚀 Sign In as Selected Student", use_container_width=True):
                s_idx = s_labels.index(picked_s)
                s_obj = student_users[s_idx]
                st.session_state["authenticated"] = True
                st.session_state["user"] = {
                    "username": s_obj["username"],
                    "role": "student",
                    "full_name": s_obj["full_name"],
                    "student_id": s_obj["student_id"]
                }
                st.rerun()
                
        st.caption("Default Credentials: **admin/admin123** | **teacher/teacher123** | **Student ID (lowercase) / student123**")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop()


# =============================================================================
# LOGGED IN USER CONTEXT & SIDEBAR
# =============================================================================
current_user = st.session_state.get("user", {})
user_role = current_user.get("role", "student")
user_full_name = current_user.get("full_name", "User")
user_student_id = current_user.get("student_id")

reminders_list = tracker.get_reminders()
pending_reminders_count = len([r for r in reminders_list if r.get("status") != "Completed"])

# Sidebar Setup
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("BCA Academic Project")
    
    # User Profile Box
    st.markdown(f"""
    <div style="background: #f1f5f9; padding: 12px 16px; border-radius: 10px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Logged In As:</div>
        <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b;">{user_full_name}</div>
        <div style="font-size: 0.9rem; color: #2563eb; font-weight: 600;">Role: {user_role.upper()}</div>
        {f'<div style="font-size: 0.85rem; color: #475569;">ID: {user_student_id}</div>' if user_student_id else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    if loaded and user_role in ["admin", "teacher"]:
        st.subheader("Model Performance")
        c_acc = meta["classifier_metrics"]["accuracy"] * 100
        r_r2 = meta["regressor_metrics"]["r2_score"]
        r_mae = meta["regressor_metrics"]["mae"]
        
        st.metric(label="Decision Tree Accuracy", value=f"{c_acc:.1f}%")
        st.metric(label="Regression R² Score", value=f"{r_r2:.3f}")
        st.metric(label="Mean Absolute Error (MAE)", value=f"{r_mae:.2f} marks")
        
        st.divider()
        st.subheader("📌 Academic Status")
        st.metric(label="Pending Reminders & Alerts", value=f"{pending_reminders_count} Active")
        
        # SQL Database Status
        sql_engine_name, sql_engine_loc = db.get_current_sql_engine()
        st.metric(label="💾 SQL Database Engine", value=sql_engine_name)
        st.caption(f"Connected: `{sql_engine_loc}`")
        
        with st.expander("⚙️ MySQL Database Setup (Optional )"):
            st.write("Connect to external MySQL / XAMPP Server:")
            m_host = st.text_input("Host", value="localhost")
            m_port = st.number_input("Port", value=3306, step=1)
            m_user = st.text_input("Username", value="root")
            m_pwd = st.text_input("Password", type="password", value="")
            m_db = st.text_input("Database Name", value="student_performance_db")
            if st.button("Connect to MySQL"):
                success, msg = db.configure_mysql(m_host, m_user, m_pwd, m_db, m_port)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
    st.caption("BCA Semester Project Evaluation & Demonstration")


# Main Header Banner
st.markdown(f"""
<div class="main-header">
    <h1>Student Performance Prediction System</h1>
    <p>Logged in as <strong>{user_full_name}</strong> ({user_role.capitalize()} Portal) • Predictive ML, Periodic Progress, Database Tracking & Reporting.</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# ROLE-BASED TAB CONFIGURATION
# =============================================================================
if user_role == "student":
    tabs = st.tabs([
        "📑 My Academic Report Card",
        "📈 My Progression Trajectory",
        "💡 Academic Advisory & Improvement"
    ])
elif user_role == "teacher":
    tabs = st.tabs([
        "🎯 Live Performance Predictor",
        "🗓️ Periodic Evaluation (Monthly / Quarterly)",
        "📜 Past Added Data & SQL Database Records",
        "⏰ Reminders & Academic Alerts",
        "📑 Student Academic Report Cards",
        "📊 Seaborn Visualizations & EDA",
        "🌳 Decision Tree Structure",
        "📁 Batch Student Prediction",
        "📈 Power BI Integration"
    ])
else:  # ADMIN ROLE (+1 ability to create/manage teachers)
    tabs = st.tabs([
        "👨‍🏫 Teacher & User Management (+1 Admin)",
        "🎯 Live Performance Predictor",
        "🗓️ Periodic Evaluation (Monthly / Quarterly)",
        "📜 Past Added Data & SQL Database Records",
        "⏰ Reminders & Academic Alerts",
        "📑 Student Academic Report Cards",
        "📊 Seaborn Visualizations & EDA",
        "🌳 Decision Tree Structure",
        "📁 Batch Student Prediction",
        "📈 Power BI Integration"
    ])


# =============================================================================
# HELPER: ACADEMIC REPORT CARD GENERATOR
# =============================================================================
def render_report_card(student_rec: dict):
    """Renders a formal, printable student performance report card."""
    pred_score = float(student_rec.get("Predicted_Score", 65.0))
    pred_tier = student_rec.get("Performance_Category", "Pass")
    att = float(student_rec.get("Attendance_Rate", 75.0))
    internal = float(student_rec.get("Internal_Assessment_Score", 30.0))
    past_score = float(student_rec.get("Past_Exam_Score", 60.0))
    study_hrs = float(student_rec.get("Study_Hours_Per_Week", 12.0))
    sleep_hrs = float(student_rec.get("Sleep_Hours_Per_Day", 7.0))
    
    # Calculate Letter Grade and GPA
    if pred_score >= 90:
        letter_grade, gpa = "O (Outstanding)", 10.0
    elif pred_score >= 80:
        letter_grade, gpa = "A+ (Excellent)", 9.0
    elif pred_score >= 70:
        letter_grade, gpa = "A (Very Good)", 8.0
    elif pred_score >= 60:
        letter_grade, gpa = "B+ (Good)", 7.0
    elif pred_score >= 50:
        letter_grade, gpa = "B (Above Average)", 6.0
    else:
        letter_grade, gpa = "F (Fail / At-Risk)", 0.0

    report_html = f"""<div class="report-card-container">
<div class="report-header">
<h2 style="color: #1e3c72; margin: 0; font-size: 1.8rem; font-weight: 800; text-align: center;">UNIVERSITY COLLEGE OF COMPUTER APPLICATIONS</h2>
<div style="font-size: 1rem; color: #475569; font-weight: 600; margin-top: 4px; text-align: center;">Department of Computer Applications • BCA Degree Programme</div>
<div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; text-align: center;">Official Student Academic Standing & Performance Report</div>
</div>

<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
<tr style="background: #f8fafc;">
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 600; width: 25%;">Student Roll / ID:</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; width: 25%; font-weight: 700; color: #1e3c72;">{student_rec.get('Student_ID')}</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 600; width: 25%;">Evaluation Date:</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; width: 25%;">{student_rec.get('Evaluation_Date')}</td>
</tr>
<tr>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 600;">Student Full Name:</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 700;">{student_rec.get('Student_Name')}</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 600;">Academic Status:</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 700; color: {'#b91c1c' if pred_tier=='At-Risk' else '#15803d'};">{student_rec.get('Status')}</td>
</tr>
</table>

<h4 style="color: #1e3c72; margin-top: 16px; margin-bottom: 8px;">1. Continuous Academic Assessment Indicators</h4>
<table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
<tr style="background: #1e3c72; color: white; font-weight: 600;">
<th style="padding: 10px; border: 1px solid #cbd5e1; text-align: left;">Assessment Component</th>
<th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center;">Recorded Metric</th>
<th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center;">Standard Benchmark</th>
<th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center;">Status</th>
</tr>
<tr>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Classroom Lecture Attendance</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700;">{att}%</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center;">75.0% Minimum</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700; color: {'#b91c1c' if att<75 else '#15803d'};">{'Deficit' if att<75 else 'Satisfactory'}</td>
</tr>
<tr style="background: #f8fafc;">
<td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Internal Assessment Examination</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700;">{internal} / 50</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center;">25.0 / 50 (Pass)</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700; color: {'#b91c1c' if internal<25 else '#15803d'};">{'Below Average' if internal<25 else 'Clear'}</td>
</tr>
<tr>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Previous Semester Baseline Score</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700;">{past_score} / 100</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center;">50.0 / 100</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700;">Passed</td>
</tr>
<tr style="background: #f8fafc;">
<td style="padding: 8px 12px; border: 1px solid #cbd5e1;">Self-Study Allocation</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center; font-weight: 700;">{study_hrs} hrs / week</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center;">14.0 hrs / week</td>
<td style="padding: 8px 12px; border: 1px solid #cbd5e1; text-align: center;">{'Adequate' if study_hrs>=12 else 'Needs Increase'}</td>
</tr>
</table>

<h4 style="color: #1e3c72; margin-top: 16px; margin-bottom: 8px;">2. Machine Learning Predictive Examination Outcome</h4>
<div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-bottom: 24px; display: flex; justify-content: space-around; text-align: center;">
<div>
<div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">PREDICTED EXAM SCORE</div>
<div style="font-size: 2rem; font-weight: 800; color: #1e3c72;">{pred_score:.1f}%</div>
</div>
<div>
<div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">ACADEMIC CLASSIFICATION</div>
<div style="font-size: 1.5rem; font-weight: 700; color: {'#b91c1c' if pred_tier=='At-Risk' else '#15803d'};">{pred_tier}</div>
</div>
<div>
<div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">GRADE & GPA SCALE</div>
<div style="font-size: 1.4rem; font-weight: 700; color: #334155;">{letter_grade} ({gpa:.1f})</div>
</div>
</div>

<h4 style="color: #1e3c72; margin-top: 16px; margin-bottom: 8px;">3. Faculty Remarks & Prescriptive Action Plan</h4>
<div style="background: #f8fafc; border-left: 4px solid #1e3c72; padding: 14px 18px; font-size: 0.95rem; margin-bottom: 30px;">
{f"• <strong>URGENT REMEDIATION:</strong> Attendance ({att}%) is critically below the 75% examination eligibility requirement. Mandatory mentor counseling scheduled.<br>" if att < 75 else "• <strong>ATTENDANCE STANDING:</strong> Attendance complies with university examination guidelines.<br>"}
{f"• <strong>STUDY TIME ADJUSTMENT:</strong> Recommend increasing self-study by at least 4 hours/week to bolster core fundamentals.<br>" if study_hrs < 12 else "• <strong>STUDY HABITS:</strong> Consistent study schedule observed.<br>"}
• <strong>OVERALL PROJECTION:</strong> Student is projected to achieve <strong>{pred_score:.1f}%</strong> ({pred_tier} Category). Maintain focus on laboratory exercises and model test submissions.
</div>

<div style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px dashed #cbd5e1; font-size: 0.9rem;">
<div style="text-align: center;">
<div style="font-weight: 700;">Prof. Rajesh Gupta</div>
<div style="color: #64748b;">Faculty Academic Mentor</div>
</div>
<div style="text-align: center;">
<div style="font-weight: 700;">Dr. M. S. Venkatesh</div>
<div style="color: #64748b;">Head of Department (BCA)</div>
</div>
<div style="text-align: center;">
<div style="font-weight: 700;">Registrar (Evaluation)</div>
<div style="color: #64748b;">Office of Academic Examination</div>
</div>
</div>
</div>"""

    if hasattr(st, "html"):
        st.html(report_html)
    else:
        st.markdown(report_html, unsafe_allow_html=True)
    
    # Download HTML Button
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Academic Report Card - {student_rec.get('Student_Name')} ({student_rec.get('Student_ID')})</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #1e293b; }}
            .container {{ border: 2px solid #1e3c72; padding: 30px; border-radius: 10px; max-width: 800px; margin: 0 auto; }}
            h2 {{ color: #1e3c72; text-align: center; margin: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 10px; }}
            th {{ background-color: #1e3c72; color: white; }}
            .metric-box {{ background: #f1f5f9; padding: 15px; text-align: center; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>UNIVERSITY COLLEGE OF COMPUTER APPLICATIONS</h2>
            <p style="text-align: center; color: #64748b; margin: 5px 0 20px 0;">Official Student Academic Standing & Performance Report</p>
            <table>
                <tr><td><strong>Student ID:</strong></td><td>{student_rec.get('Student_ID')}</td><td><strong>Date:</strong></td><td>{student_rec.get('Evaluation_Date')}</td></tr>
                <tr><td><strong>Student Name:</strong></td><td>{student_rec.get('Student_Name')}</td><td><strong>Academic Status:</strong></td><td>{student_rec.get('Status')}</td></tr>
            </table>
            <h3>Assessment Indicators</h3>
            <table>
                <tr><th>Component</th><th>Recorded</th><th>Benchmark</th></tr>
                <tr><td>Attendance Rate</td><td>{att}%</td><td>75%</td></tr>
                <tr><td>Internal Assessment</td><td>{internal}/50</td><td>25/50</td></tr>
                <tr><td>Past Semester Exam</td><td>{past_score}/100</td><td>50/100</td></tr>
            </table>
            <div class="metric-box">
                <h3>Predicted Score: {pred_score:.1f}% | Classification: {pred_tier}</h3>
                <p>Letter Grade: {letter_grade} (GPA: {gpa:.1f})</p>
            </div>
            <p><strong>Faculty Action Plan:</strong> Evaluation completed by Decision Tree Predictive Model. Student advised to adhere to study schedule.</p>
        </div>
    </body>
    </html>
    """
    st.download_button(
        label=f"🖨️ Download Printable Report Card (HTML) for {student_rec.get('Student_Name')}",
        data=html_content.encode('utf-8'),
        file_name=f"Report_Card_{student_rec.get('Student_ID')}.html",
        mime="text/html",
        use_container_width=True
    )


# =============================================================================
# STUDENT ROLE VIEWS
# =============================================================================
if user_role == "student":
    with tabs[0]:
        st.subheader("🎓 My Official Academic Report Card")
        # Fetch student record from SQL database
        all_recs = db.fetch_all_student_records()
        my_rec = pd.DataFrame()
        if not all_recs.empty:
            if user_student_id:
                my_rec = all_recs[all_recs["Student_ID"].astype(str).str.strip().str.upper() == str(user_student_id).strip().upper()]
            if my_rec.empty and user_full_name:
                my_rec = all_recs[all_recs["Student_Name"].astype(str).str.contains(user_full_name.split()[0], case=False, na=False)]
        
        if not my_rec.empty:
            render_report_card(my_rec.iloc[0].to_dict())
        else:
            # Fallback sample record
            sample_my_rec = {
                "Student_ID": user_student_id,
                "Student_Name": user_full_name,
                "Evaluation_Date": datetime.date.today().strftime("%Y-%m-%d"),
                "Attendance_Rate": 88.0,
                "Study_Hours_Per_Week": 18.5,
                "Internal_Assessment_Score": 42.0,
                "Past_Exam_Score": 76.0,
                "Sleep_Hours_Per_Day": 7.5,
                "Predicted_Score": 79.4,
                "Performance_Category": "Merit",
                "Status": "On Track"
            }
            render_report_card(sample_my_rec)

    with tabs[1]:
        st.subheader("📈 My Academic Progression Trajectory")
        p_df = tracker.get_periodic_evaluations()
        my_periodic = p_df[p_df["Student_Name"].str.contains(user_full_name.split()[0], case=False, na=False)]
        
        if not my_periodic.empty:
            fig = px.line(
                my_periodic[my_periodic["Cycle_Type"] == "Monthly"],
                x="Period", y="Predicted_Score",
                title=f"Predicted Marks Trend across Semesters/Months - {user_full_name}",
                markers=True
            )
            fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Distinction Target (75%+)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(my_periodic, use_container_width=True, hide_index=True)
        else:
            st.info("No periodic evaluations recorded for your account yet.")

    with tabs[2]:
        st.subheader("💡 Personalized Academic Advisory & Study Strategy")
        st.markdown("""
        #### Recommendations to Boost Your Performance:
        1. **Attendance Maintenance:** Maintain your attendance above **85%** to ensure eligibility for internal marks bonus.
        2. **Weekly Study Habit:** Commit to **2 hours of self-study every evening** focusing on Data Structures and Web Development.
        3. **Peer Mentorship:** Attend department code clubs and laboratory practice sessions.
        4. **Sleep Schedule:** Ensure consistent 7 to 8 hours of sleep before internal test weeks.
        """)
        
    st.stop()
    sys.exit(0)


# =============================================================================
# ADMIN SPECIAL FEATURE: TEACHER & USER MANAGEMENT (+1 ABILITY)
# =============================================================================
tab_offset = 0
if user_role == "admin":
    with tabs[0]:
        st.subheader("👨‍🏫 Teacher & User Management ")
        st.markdown("As the **System Administrator**, you have the exclusive authority to **create, manage, and revoke Teacher and Faculty accounts**.")
        
        adm_col1, adm_col2 = st.columns([1.2, 1.8])
        
        with adm_col1:
            st.markdown("#### ➕ Create New Teacher / Faculty Account")
            with st.form("create_teacher_form", clear_on_submit=True):
                t_user = st.text_input("Username", placeholder="e.g., prof_sharma")
                t_name = st.text_input("Full Name & Title", placeholder="e.g., Prof. Anjali Sharma (AI/ML)")
                t_pwd = st.text_input("Initial Password", type="password", placeholder="e.g., faculty@123")
                t_role = st.selectbox("Assign System Role:", ["teacher", "admin", "student"])
                t_stud_id = None
                if t_role == "student":
                    t_stud_id = st.text_input("Associated Student ID:", value="STU1300")
                    
                submit_t = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
                if submit_t:
                    if not t_user or not t_name or not t_pwd:
                        st.warning("Please fill in all username, name, and password fields.")
                    else:
                        ok, msg = auth.create_user(t_user, t_pwd, t_role, t_name, t_stud_id)
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(msg)
                            
        with adm_col2:
            st.markdown("#### 📋 Registered System Users & Teachers")
            all_users = auth.get_all_users()
            u_df = pd.DataFrame(all_users)
            st.dataframe(u_df[["id", "username", "role", "full_name", "student_id", "created_at"]], hide_index=True, use_container_width=True)
            
            # Delete User Section
            st.markdown("##### 🗑️ Revoke / Delete User Account")
            d_u_col1, d_u_col2 = st.columns([2, 1])
            with d_u_col1:
                deletable = [u["username"] for u in all_users if u["username"] != "admin"]
                if deletable:
                    u_to_del = st.selectbox("Select Account to Remove:", deletable)
                    if st.button("Confirm Delete Account", type="secondary"):
                        d_ok, d_msg = auth.delete_user(u_to_del)
                        if d_ok:
                            st.warning(d_msg)
                            st.rerun()
                        else:
                            st.error(d_msg)
                else:
                    st.info("No non-admin accounts to delete.")
                    
    tab_offset = 1  # Shift tab indexes for admin


# =============================================================================
# TAB: LIVE PERFORMANCE PREDICTOR (Teacher & Admin)
# =============================================================================
with tabs[tab_offset + 0]:
    st.subheader("Interactive Student Profile Evaluation")
    st.write("Enter student identification, academic history, and behavioral habits to predict semester examination outcomes.")
    
    # Student ID & Name Row
    id_col1, id_col2 = st.columns([1, 1])
    with id_col1:
        student_id_input = st.text_input("Student Roll / ID Number", value="STU1205")
    with id_col2:
        student_name_input = st.text_input("Student Full Name", value="Karan Mehra")
        
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📚 Academic Background")
        past_score = st.slider("Past Semester Exam Score (out of 100)", min_value=30.0, max_value=100.0, value=68.0, step=0.5)
        internal_score = st.slider("Internal Assessment Marks (out of 50)", min_value=10.0, max_value=50.0, value=34.0, step=0.5)
        assignment_rate = st.slider("Assignment Completion Rate (%)", min_value=40.0, max_value=100.0, value=80.0, step=1.0)
        attendance = st.slider("Class Attendance Rate (%)", min_value=40.0, max_value=100.0, value=78.0, step=0.5)

    with col2:
        st.markdown("#### ⏳ Study & Lifestyle Factors")
        study_hours = st.slider("Weekly Study Hours (hrs/week)", min_value=2.0, max_value=35.0, value=14.0, step=0.5)
        sleep_hours = st.slider("Average Sleep Hours / Day", min_value=4.0, max_value=10.0, value=7.0, step=0.5)
        tutoring = st.selectbox("Enrolled in Extra Tutoring / Coaching?", ["No", "Yes"])
        extracurricular = st.selectbox("Participates in Extracurricular Activities?", ["Yes", "No"])

    with col3:
        st.markdown("#### 👤 Demographics & Environment")
        age = st.selectbox("Student Age", [18, 19, 20, 21, 22, 23], index=1)
        gender = st.selectbox("Gender", ["Female", "Male"])
        parental_edu = st.selectbox("Parental Education Level", ["High School", "Diploma", "Bachelor", "Master"], index=2)
        internet = st.selectbox("High-Speed Internet Access at Home?", ["Yes", "No"])

    st.write("")
    predict_btn = st.button("🚀 Evaluate Student Performance", type="primary", use_container_width=True)
    
    if predict_btn and loaded:
        input_data = {
            "Age": [age],
            "Gender": [encoders["Gender"].transform([gender])[0]],
            "Parental_Education": [encoders["Parental_Education"].transform([parental_edu])[0]],
            "Study_Hours_Per_Week": [study_hours],
            "Attendance_Rate": [attendance],
            "Past_Exam_Score": [past_score],
            "Internal_Assessment_Score": [internal_score],
            "Assignment_Completion_Rate": [assignment_rate],
            "Tutoring_Classes": [encoders["Tutoring_Classes"].transform([tutoring])[0]],
            "Internet_Access": [encoders["Internet_Access"].transform([internet])[0]],
            "Extracurricular_Activities": [encoders["Extracurricular_Activities"].transform([extracurricular])[0]],
            "Sleep_Hours_Per_Day": [sleep_hours]
        }
        input_df = pd.DataFrame(input_data)
        
        pred_tier = clf.predict(input_df)[0]
        pred_score = float(reg.predict(input_df)[0])
        pred_score = np.clip(pred_score, 0.0, 100.0)
        
        # Save evaluation in session state
        st.session_state["latest_evaluation"] = {
            "Evaluation_ID": f"EV-{np.random.randint(1000, 9999)}",
            "Evaluation_Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Student_ID": student_id_input,
            "Student_Name": student_name_input,
            "Attendance_Rate": attendance,
            "Study_Hours_Per_Week": study_hours,
            "Internal_Assessment_Score": internal_score,
            "Past_Exam_Score": past_score,
            "Sleep_Hours_Per_Day": sleep_hours,
            "Predicted_Score": round(pred_score, 1),
            "Performance_Category": pred_tier,
            "Status": "At-Risk" if pred_tier == "At-Risk" else ("Distinction" if pred_tier == "Distinction" else "On Track")
        }

    if "latest_evaluation" in st.session_state:
        eval_data = st.session_state["latest_evaluation"]
        pred_tier = eval_data["Performance_Category"]
        pred_score = eval_data["Predicted_Score"]
        
        st.divider()
        st.markdown(f"### 📋 Prediction Results for {eval_data['Student_Name']} ({eval_data['Student_ID']})")
        
        res_col1, res_col2, res_col3 = st.columns([1.2, 1, 1.4])
        
        with res_col1:
            st.markdown("#### Predicted Academic Tier")
            if pred_tier == "Distinction":
                badge_html = '<span class="badge-distinction">🌟 Distinction (>=80%)</span>'
            elif pred_tier == "Merit":
                badge_html = '<span class="badge-merit">🥇 Merit (65% - 79%)</span>'
            elif pred_tier == "Pass":
                badge_html = '<span class="badge-pass">🥈 Second Class / Pass (50% - 64%)</span>'
            else:
                badge_html = '<span class="badge-risk">⚠️ At-Risk / Needs Intervention (<50%)</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
            
            st.write("")
            st.metric(
                label="Estimated Final Score",
                value=f"{pred_score:.1f} / 100",
                delta=f"{pred_score - eval_data['Past_Exam_Score']:+.1f} vs Past Exam"
            )
            st.progress(pred_score / 100.0)

        with res_col2:
            st.markdown("#### Student Factor Profile")
            st.write(f"• **Attendance:** {eval_data['Attendance_Rate']}%")
            st.write(f"• **Weekly Study:** {eval_data['Study_Hours_Per_Week']} hrs")
            st.write(f"• **Internal Marks:** {eval_data['Internal_Assessment_Score']}/50")
            st.write(f"• **Sleep Hours:** {eval_data['Sleep_Hours_Per_Day']} hrs/day")
            
            # Action Buttons with Duplicate Check and Reset
            st.write("")
            btn_s1, btn_s2 = st.columns([1.5, 1])
            with btn_s1:
                if st.button("💾 Save to SQL DB", use_container_width=True):
                    exists, ex_name, ex_date = db.check_student_exists(eval_data['Student_ID'])
                    if exists:
                        st.error(f"⚠️ Duplicate: Student ID '{eval_data['Student_ID']}' already exists for student '{ex_name}' in database!")
                    else:
                        tracker.add_evaluation_record(eval_data)
                        auth.auto_create_student_account(eval_data['Student_ID'], eval_data['Student_Name'], "student123")
                        st.success(f"✅ Saved {eval_data['Student_Name']} ({eval_data['Student_ID']}) to database! Student login account auto-created (Username: '{eval_data['Student_ID'].strip().lower()}' / Password: 'student123').")
                        st.session_state.pop("latest_evaluation", None)
                        st.rerun()
            with btn_s2:
                if st.button("🔄 Clear Form", use_container_width=True):
                    st.session_state.pop("latest_evaluation", None)
                    st.rerun()
                
            if eval_data['Attendance_Rate'] < 75.0 or pred_tier == "At-Risk":
                if st.button("🔔 Set Academic Alert Reminder", use_container_width=True):
                    new_rem = {
                        "id": f"REM-{np.random.randint(100, 999)}",
                        "title": f"Intervention Alert: {eval_data['Student_Name']}",
                        "student_id": eval_data['Student_ID'],
                        "student_name": eval_data['Student_Name'],
                        "type": "Attendance Deficit" if eval_data['Attendance_Rate'] < 75 else "Academic Failure Risk",
                        "frequency": "Weekly",
                        "due_date": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                        "priority": "High",
                        "status": "Pending",
                        "message": f"Student scored {pred_score:.1f}% (Predicted: {pred_tier}) with attendance {eval_data['Attendance_Rate']}%. Immediate counseling required."
                    }
                    tracker.add_reminder(new_rem)
                    st.warning(f"High-priority reminder created in Reminders Tab!")

        with res_col3:
            st.markdown("#### 💡 Tailored Academic Recommendations")
            recs = []
            if eval_data['Attendance_Rate'] < 75.0:
                recs.append(f"**Critical Attendance Alert:** Current attendance ({eval_data['Attendance_Rate']}%) is below the university minimum 75%. Prioritize lecture attendance to prevent debarment.")
            if eval_data['Study_Hours_Per_Week'] < 10.0:
                recs.append(f"**Increase Study Time:** Current {eval_data['Study_Hours_Per_Week']} hrs/week is below the recommended 12-16 hrs. Dedicating 1 extra hour per day will boost score by approx 4-6 marks.")
            if eval_data['Sleep_Hours_Per_Day'] < 6.0:
                recs.append("**Sleep Hygiene:** Student averages less than 6 hours of sleep. Insufficient rest impairs cognitive retention during internal exams.")
            if eval_data['Internal_Assessment_Score'] < 25.0:
                recs.append("**Remedial Support:** Internal score is low. Attend faculty doubt-clearing sessions and submit mock assignments.")
            if not recs:
                recs.append("**Excellent Academic Health:** Student maintains solid attendance and study habits. Encourage taking up advanced competitive coding or certifications.")
                
            for rec in recs:
                st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)


# =============================================================================
# TAB: PERIODIC EVALUATION (MONTHLY / QUARTERLY)
# =============================================================================
with tabs[tab_offset + 1]:
    st.subheader("Periodic Progression Tracking: Monthly & Quarterly Evaluations")
    st.write("Monitor student trajectories over time to verify whether academic standing is **improving, stagnant, or deteriorating** across monthly reviews or quarterly terms.")
    
    # Cadence Switcher
    cycle_choice = st.radio(
        "Select Evaluation Cadence:",
        ["📅 Monthly Evaluation Cycle", "📊 Quarterly Evaluation Cycle"],
        horizontal=True
    )
    cycle_filter = "Monthly" if "Monthly" in cycle_choice else "Quarterly"
    
    p_df = tracker.get_periodic_evaluations()
    filtered_p_df = p_df[p_df["Cycle_Type"] == cycle_filter]
    
    # Student Selector
    available_students = sorted(list(filtered_p_df["Student_Name"].unique()))
    if not available_students:
        available_students = ["Aarav Sharma"]
        
    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        selected_student = st.selectbox("Select Student to Inspect:", available_students)
        student_records = filtered_p_df[filtered_p_df["Student_Name"] == selected_student].copy()
        
        if len(student_records) >= 2:
            first_score = student_records.iloc[0]["Predicted_Score"]
            last_score = student_records.iloc[-1]["Predicted_Score"]
            score_delta = last_score - first_score
            first_att = student_records.iloc[0]["Attendance"]
            last_att = student_records.iloc[-1]["Attendance"]
            att_delta = last_att - first_att
            
            st.metric(
                label=f"Net Score Delta ({student_records.iloc[0]['Period']} → {student_records.iloc[-1]['Period']})",
                value=f"{last_score:.1f}%",
                delta=f"{score_delta:+.1f}% Total Shift"
            )
            st.metric(
                label=f"Attendance Trend",
                value=f"{last_att:.1f}%",
                delta=f"{att_delta:+.1f}%"
            )
            
            if score_delta >= 3:
                st.success("📈 **Positive Trajectory:** Continuous improvement across review periods.")
            elif score_delta <= -3:
                st.error("📉 **Negative Trajectory:** Student shows academic decline. Immediate counseling advised.")
            else:
                st.info("⚖️ **Stable Trajectory:** Consistent performance across evaluation cycles.")
        else:
            st.info("Need at least 2 period records to compute net trajectory delta.")

    with p_col2:
        if not student_records.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=student_records["Period"],
                y=student_records["Predicted_Score"],
                mode="lines+markers",
                name="Predicted Exam Score (%)",
                line=dict(color="#2563eb", width=3),
                marker=dict(size=9, symbol="diamond")
            ))
            fig.add_trace(go.Scatter(
                x=student_records["Period"],
                y=student_records["Attendance"],
                mode="lines+markers",
                name="Attendance Rate (%)",
                line=dict(color="#10b981", width=2, dash="dash"),
                marker=dict(size=7)
            ))
            
            fig.add_hline(y=75, line_width=1, line_dash="dot", line_color="orange", annotation_text="75% Attendance Threshold")
            fig.add_hline(y=50, line_width=1, line_dash="dot", line_color="red", annotation_text="50% Pass Cutoff")
            
            fig.update_layout(
                title=f"{selected_student} - {cycle_filter} Academic Trajectory",
                xaxis_title="Evaluation Period",
                yaxis_title="Percentage (%)",
                yaxis=dict(range=[20, 100]),
                height=350,
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    st.divider()
    st.markdown(f"#### 📋 Historical Period Records for {selected_student}")
    st.dataframe(student_records[["Period", "Attendance", "Study_Hours", "Internal_Score", "Predicted_Score", "Tier"]], hide_index=True, use_container_width=True)
    
    # Form to Log New Periodic Entry
    with st.expander(f"➕ Log New {cycle_filter} Evaluation Entry for a Student"):
        with st.form("periodic_form", clear_on_submit=True):
            form_col1, form_col2, form_col3 = st.columns(3)
            with form_col1:
                log_name = st.text_input("Student Name", value=selected_student)
                log_id = st.text_input("Student ID", value="STU1042")
                period_name = st.text_input("Period Name", value="Month 5 (Aug)" if cycle_filter == "Monthly" else "Q3 (Pre-Univ)")
            with form_col2:
                log_att = st.slider("Attendance Rate (%)", 40.0, 100.0, 85.0, 0.5)
                log_study = st.slider("Study Hours / Week", 2.0, 35.0, 16.0, 0.5)
            with form_col3:
                log_int = st.slider("Internal Score (out of 50)", 10.0, 50.0, 38.0, 0.5)
                log_past = st.slider("Past Score Baseline", 30.0, 100.0, 70.0, 0.5)
                
            submit_periodic = st.form_submit_button("Record Periodic Evaluation", type="primary")
            if submit_periodic and loaded:
                sample_input = {
                    "Age": [20], "Gender": [0], "Parental_Education": [1],
                    "Study_Hours_Per_Week": [log_study], "Attendance_Rate": [log_att],
                    "Past_Exam_Score": [log_past], "Internal_Assessment_Score": [log_int],
                    "Assignment_Completion_Rate": [85.0], "Tutoring_Classes": [0],
                    "Internet_Access": [1], "Extracurricular_Activities": [0],
                    "Sleep_Hours_Per_Day": [7.0]
                }
                calc_score = round(float(reg.predict(pd.DataFrame(sample_input))[0]), 1)
                calc_tier = clf.predict(pd.DataFrame(sample_input))[0]
                
                new_entry = {
                    "Student_ID": log_id, "Student_Name": log_name, "Cycle_Type": cycle_filter,
                    "Period": period_name, "Attendance": log_att, "Study_Hours": log_study,
                    "Internal_Score": log_int, "Predicted_Score": calc_score, "Tier": calc_tier
                }
                tracker.add_periodic_evaluation(new_entry)
                st.success(f"Recorded new {cycle_filter} evaluation for {log_name}: Predicted {calc_score}% ({calc_tier})!")
                st.rerun()


# =============================================================================
# TAB: PAST ADDED DATA & SQL DATABASE RECORDS (Teacher & Admin)
# =============================================================================
with tabs[tab_offset + 2]:
    st.subheader("📜 Past Added Data & SQL Database Records")
    engine_name, engine_path = db.get_current_sql_engine()
    st.info(f"💾 **Active SQL Database:** `{engine_name}` | Location/Target: `{engine_path}` | Table: `student_evaluations`")
    
    # Expander to Add New Student Data to SQL DB
    with st.expander("➕ Add New Student Record to SQL Database", expanded=False):
        st.markdown("Enter student profile to compute prediction and save directly to the SQL database.")
        with st.form("add_sql_student_form", clear_on_submit=True):
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                new_s_id = st.text_input("Student ID / Roll No.", placeholder="e.g., STU1208")
                new_s_name = st.text_input("Full Name", placeholder="e.g., Neha Singh")
                new_age = st.selectbox("Age", [18, 19, 20, 21, 22, 23], index=2)
                new_gender = st.selectbox("Gender", ["Female", "Male"])
            with s_col2:
                new_att = st.slider("Attendance Rate (%)", 40.0, 100.0, 82.0, 0.5)
                new_study = st.slider("Weekly Study Hours", 2.0, 35.0, 15.0, 0.5)
                new_internal = st.slider("Internal Score (/50)", 10.0, 50.0, 36.0, 0.5)
                new_past = st.slider("Past Exam Score (/100)", 30.0, 100.0, 72.0, 0.5)
            with s_col3:
                new_parent_edu = st.selectbox("Parental Education", ["High School", "Diploma", "Bachelor", "Master"], index=2)
                new_tutoring = st.selectbox("Tutoring Classes?", ["No", "Yes"])
                new_internet = st.selectbox("Internet Access?", ["Yes", "No"])
                new_sleep = st.slider("Sleep Hours / Day", 4.0, 10.0, 7.5, 0.5)
                
            submit_new_sql = st.form_submit_button("💾 Save Record to SQL Database (Auto-Clears Form)", type="primary", use_container_width=True)
            if submit_new_sql and loaded:
                if not new_s_id or not new_s_name:
                    st.warning("⚠️ Please provide both a Student ID and Full Name before saving.")
                else:
                    exists, existing_name, existing_date = db.check_student_exists(new_s_id)
                    if exists:
                        st.error(f"⚠️ Duplicate Detected: Student ID '{new_s_id}' already exists for student '{existing_name}' (Recorded: {existing_date})! Please use a unique Student ID.")
                    else:
                        sample_data = {
                            "Age": [new_age], "Gender": [encoders["Gender"].transform([new_gender])[0]],
                            "Parental_Education": [encoders["Parental_Education"].transform([new_parent_edu])[0]],
                            "Study_Hours_Per_Week": [new_study], "Attendance_Rate": [new_att],
                            "Past_Exam_Score": [new_past], "Internal_Assessment_Score": [new_internal],
                            "Assignment_Completion_Rate": [85.0], "Tutoring_Classes": [encoders["Tutoring_Classes"].transform([new_tutoring])[0]],
                            "Internet_Access": [encoders["Internet_Access"].transform([new_internet])[0]],
                            "Extracurricular_Activities": [0], "Sleep_Hours_Per_Day": [new_sleep]
                        }
                        calc_score = round(float(reg.predict(pd.DataFrame(sample_data))[0]), 1)
                        calc_tier = clf.predict(pd.DataFrame(sample_data))[0]
                        status_lbl = "At-Risk" if calc_tier == "At-Risk" else ("Distinction" if calc_tier == "Distinction" else "On Track")
                        
                        sql_record = {
                            "Evaluation_ID": f"EV-{np.random.randint(2000, 9999)}",
                            "Evaluation_Date": datetime.date.today().strftime("%Y-%m-%d"),
                            "Student_ID": new_s_id.strip(), "Student_Name": new_s_name.strip(),
                            "Attendance_Rate": new_att, "Study_Hours_Per_Week": new_study,
                            "Internal_Assessment_Score": new_internal, "Past_Exam_Score": new_past,
                            "Sleep_Hours_Per_Day": new_sleep, "Predicted_Score": calc_score,
                            "Performance_Category": calc_tier, "Status": status_lbl
                        }
                        db.insert_student_record(sql_record)
                        auth.auto_create_student_account(new_s_id.strip(), new_s_name.strip(), "student123")
                        st.session_state["tab3_success"] = f"✅ Record for {new_s_name} ({new_s_id}) successfully inserted! Student account auto-created (Username: '{new_s_id.strip().lower()}' / Password: 'student123')."
                        st.rerun()

    if "tab3_success" in st.session_state:
        st.success(st.session_state.pop("tab3_success"))

    # Fetch from SQL DB
    hist_df = db.fetch_all_student_records()
    
    # KPI Metrics Row
    h_m1, h_m2, h_m3, h_m4, h_m5 = st.columns(5)
    total_evals = len(hist_df)
    dist_count = len(hist_df[hist_df["Performance_Category"] == "Distinction"])
    merit_count = len(hist_df[hist_df["Performance_Category"] == "Merit"])
    pass_count = len(hist_df[hist_df["Performance_Category"] == "Pass"])
    risk_count = len(hist_df[hist_df["Performance_Category"] == "At-Risk"])
    
    h_m1.metric("Total in SQL DB", f"{total_evals}")
    h_m2.metric("Distinction", f"{dist_count}")
    h_m3.metric("Merit", f"{merit_count}")
    h_m4.metric("Pass", f"{pass_count}")
    h_m5.metric("At-Risk", f"{risk_count}", delta=f"{risk_count} Urgent" if risk_count > 0 else "0", delta_color="inverse")
    
    st.divider()
    
    # Search and Filter Toolbar
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search by Student Name or Student ID", placeholder="e.g., Aarav or STU1105")
    with f_col2:
        tier_filter = st.selectbox("Filter by Academic Tier:", ["All Tiers", "Distinction", "Merit", "Pass", "At-Risk"])
        
    filtered_history = hist_df.copy()
    if search_query:
        filtered_history = filtered_history[
            filtered_history["Student_Name"].str.contains(search_query, case=False, na=False) |
            filtered_history["Student_ID"].str.contains(search_query, case=False, na=False)
        ]
    if tier_filter != "All Tiers":
        filtered_history = filtered_history[filtered_history["Performance_Category"] == tier_filter]
        
    st.dataframe(filtered_history, use_container_width=True, hide_index=True)
    
    # Action buttons
    d_col1, d_col2 = st.columns([1, 1])
    with d_col1:
        csv_hist = filtered_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export SQL Records as CSV",
            data=csv_hist,
            file_name="sql_student_evaluation_records.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d_col2:
        if not hist_df.empty:
            del_id = st.selectbox("Select Record to Delete from SQL DB:", hist_df["Evaluation_ID"] + " - " + hist_df["Student_Name"])
            if st.button("🗑️ Delete Selected Record from SQL DB"):
                raw_eval_id = del_id.split(" - ")[0]
                db.delete_student_record(raw_eval_id)
                st.warning(f"Deleted record {raw_eval_id} from SQL database!")
                st.rerun()

    # Clear All Saved Records Tool
    with st.expander("🧹 Clear All Saved Database Records (Database Reset)"):
        st.warning("⚠️ **Danger Zone:** This will delete all student records saved in the SQL database table.")
        c_confirm = st.checkbox("I confirm that I want to clear all records from the SQL database.")
        if st.button("🚨 Clear All Records Now", type="secondary", disabled=not c_confirm):
            db.clear_all_student_records()
            st.success("All records have been successfully cleared from the SQL database!")
            st.rerun()


# =============================================================================
# TAB: REMINDERS & ACADEMIC ALERTS (Teacher & Admin)
# =============================================================================
with tabs[tab_offset + 3]:
    st.subheader("Academic Reminders & Early-Warning Alert Center")
    st.write("Schedule review deadlines, set monthly/quarterly evaluation reminders, and track attendance warning alerts.")
    
    rem_active = [r for r in tracker.get_reminders() if r.get("status") != "Completed"]
    rem_completed = [r for r in tracker.get_reminders() if r.get("status") == "Completed"]
    
    # Early Warning Scanner
    st.markdown("#### ⚡ Quick Actions")
    scan_col1, scan_col2 = st.columns([1.5, 1])
    with scan_col1:
        st.write("Scan the evaluation history database to automatically trigger intervention reminders for students with attendance < 75% or scores < 50%.")
    with scan_col2:
        if st.button("🚨 Auto-Scan & Create Alerts for At-Risk Students", type="primary", use_container_width=True):
            h_df = db.fetch_all_student_records()
            flagged = h_df[(h_df["Attendance_Rate"] < 75.0) | (h_df["Predicted_Score"] < 50.0)]
            created_count = 0
            for _, row in flagged.iterrows():
                alert_id = f"REM-AUTO-{np.random.randint(100, 999)}"
                new_alert = {
                    "id": alert_id,
                    "title": f"Intervention Alert: {row['Student_Name']}",
                    "student_id": row['Student_ID'],
                    "student_name": row['Student_Name'],
                    "type": "Early-Warning Intervention",
                    "frequency": "Immediate",
                    "due_date": (datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "status": "Pending",
                    "message": f"Student flagged with {row['Attendance_Rate']}% attendance and predicted score {row['Predicted_Score']}%. Immediate faculty counseling required."
                }
                tracker.add_reminder(new_alert)
                created_count += 1
            st.success(f"Scanned complete history: Created {created_count} early-warning reminders!")
            st.rerun()
            
    st.divider()
    
    r_tab1, r_tab2 = st.columns([1.8, 1.2])
    
    with r_tab1:
        st.markdown(f"#### 🔔 Active Reminders ({len(rem_active)})")
        if not rem_active:
            st.info("No pending reminders! All evaluations and follow-ups are up to date.")
        else:
            for rem in rem_active:
                priority_class = "priority-high" if rem.get("priority") == "High" else ("priority-medium" if rem.get("priority") == "Medium" else "priority-low")
                priority_badge = "🔴 High Priority" if rem.get("priority") == "High" else ("🟡 Medium Priority" if rem.get("priority") == "Medium" else "🟢 Low Priority")
                
                with st.container():
                    st.markdown(f"""
                    <div class="reminder-card {priority_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 1.1rem; color: #1e293b;">{rem.get('title')}</strong>
                            <span style="font-size: 0.85rem; font-weight: 700;">{priority_badge}</span>
                        </div>
                        <div style="color: #64748b; font-size: 0.9rem; margin-top: 4px;">
                            <strong>Target:</strong> {rem.get('student_name')} ({rem.get('student_id')}) | <strong>Cadence:</strong> {rem.get('frequency')} | <strong>Due Date:</strong> {rem.get('due_date')}
                        </div>
                        <div style="margin-top: 8px; font-size: 0.95rem; color: #334155;">
                            {rem.get('message')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
                    with btn_col1:
                        if st.button("✅ Resolve", key=f"resolve_{rem['id']}"):
                            tracker.update_reminder_status(rem['id'], "Completed")
                            st.success("Reminder marked as resolved!")
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"del_{rem['id']}"):
                            tracker.delete_reminder(rem['id'])
                            st.rerun()
                    st.write("")

        if rem_completed:
            with st.expander(f"View Resolved Reminders ({len(rem_completed)})"):
                for crem in rem_completed:
                    st.write(f"• **{crem.get('title')}** (Target: {crem.get('student_name')}) - Completed")

    with r_tab2:
        st.markdown("#### ➕ Create Custom Reminder")
        with st.form("new_reminder_form"):
            rem_title = st.text_input("Reminder Title", value="Conduct Monthly Evaluation Review")
            rem_target = st.text_input("Student Name or Cohort", value="BCA 5th Sem Class")
            rem_target_id = st.text_input("Student ID (or ALL)", value="ALL")
            rem_type = st.selectbox("Category:", ["Periodic Review", "Attendance Deficit", "Academic Remediation", "Assignment Deadline", "Parent-Teacher Meeting"])
            rem_cadence = st.selectbox("Frequency / Schedule:", ["Monthly", "Quarterly", "Weekly", "One-Time Deadline"])
            rem_due = st.date_input("Due Date:", value=datetime.date.today() + datetime.timedelta(days=14))
            rem_prio = st.selectbox("Priority Level:", ["High", "Medium", "Low"], index=1)
            rem_msg = st.text_area("Alert Message / Action Plan:", value="Submit internal assessment marks and update periodic progression tracker.")
            
            submit_rem = st.form_submit_button("Schedule Reminder", type="primary", use_container_width=True)
            if submit_rem:
                new_item = {
                    "id": f"REM-{np.random.randint(1000, 9999)}",
                    "title": rem_title, "student_id": rem_target_id, "student_name": rem_target,
                    "type": rem_type, "frequency": rem_cadence, "due_date": rem_due.strftime("%Y-%m-%d"),
                    "priority": rem_prio, "status": "Pending", "message": rem_msg
                }
                tracker.add_reminder(new_item)
                st.success("Custom reminder successfully scheduled!")
                st.rerun()


# =============================================================================
# TAB: STUDENT ACADEMIC REPORT CARDS (Teacher & Admin)
# =============================================================================
with tabs[tab_offset + 4]:
    st.subheader("📑 Student Academic Standing & Report Cards")
    st.write("Generate and export formal, comprehensive student report cards for semester reviews and parent counseling.")
    
    sql_students = db.fetch_all_student_records()
    
    if sql_students.empty:
        st.warning("No student evaluation records found in SQL database. Please add student evaluations first.")
    else:
        student_picker = st.selectbox(
            "Select Student to Generate Report Card:",
            sql_students["Student_ID"] + " - " + sql_students["Student_Name"]
        )
        picked_id = student_picker.split(" - ")[0]
        selected_rec = sql_students[sql_students["Student_ID"] == picked_id].iloc[0].to_dict()
        
        st.write("")
        render_report_card(selected_rec)


# =============================================================================
# TAB: SEABORN VISUALIZATIONS & EDA
# =============================================================================
with tabs[tab_offset + 5]:
    st.subheader("Exploratory Data Analysis (EDA) Visualizations")
    st.write("Publication-grade statistical plots generated with **Seaborn** and **Matplotlib**.")
    
    vis_files = {
        "Correlation Heatmap": (
            "visualizations/correlation_heatmap.png",
            "Demonstrates Pearson correlation among numerical attributes. Attendance, internal scores, and past scores show strong positive correlation with final grades."
        ),
        "Attendance vs Final Score": (
            "visualizations/attendance_vs_performance.png",
            "Scatter plot with linear regression trendline highlighting that students with >75% attendance consistently cross the passing threshold."
        ),
        "Study Hours Distribution": (
            "visualizations/study_hours_distribution.png",
            "Kernel Density Estimation (KDE) and histogram illustrating study time variance between passed students and students at risk."
        ),
        "Parental Education & Tutoring": (
            "visualizations/grade_distribution_by_parental_edu.png",
            "Boxplot comparing final marks grouped by parental educational background and private tutoring attendance."
        ),
        "Performance Category Breakdown": (
            "visualizations/performance_category_breakdown.png",
            "Class distribution showing the percentage of students in Distinction, Merit, Pass, and At-Risk tiers."
        ),
        "Sleep Hours vs Academic Score": (
            "visualizations/sleep_vs_performance.png",
            "Non-linear trend showcasing the optimal sleep window between 6.5 and 8.5 hours for maximum academic attainment."
        )
    }
    
    selected_vis = st.selectbox("Choose Visualization to Inspect:", list(vis_files.keys()))
    img_path, description = vis_files[selected_vis]
    
    if os.path.exists(img_path):
        st.image(img_path, caption=selected_vis, use_container_width=True)
        st.info(f"**Key Academic Insight:** {description}")
    else:
        st.warning(f"Visualization {img_path} not found. Please run 'python -m src.eda' to generate plots.")


# =============================================================================
# TAB: DECISION TREE STRUCTURE
# =============================================================================
with tabs[tab_offset + 6]:
    st.subheader("Machine Learning: Decision Tree Architecture")
    st.write("Decision Trees offer high interpretability by producing explicit if-then decision rules.")
    
    dt_col1, dt_col2 = st.columns([1.5, 1])
    
    with dt_col1:
        tree_img = "visualizations/decision_tree_structure.png"
        if os.path.exists(tree_img):
            st.image(tree_img, caption="Trained Decision Tree Classifier Flow (Top Levels)", use_container_width=True)
        else:
            st.warning("Decision tree diagram not found. Run 'python -m src.train' to generate.")
            
    with dt_col2:
        feat_img = "visualizations/feature_importance.png"
        if os.path.exists(feat_img):
            st.image(feat_img, caption="Gini / Entropy Feature Importance Weights", use_container_width=True)
        
        cm_img = "visualizations/confusion_matrix.png"
        if os.path.exists(cm_img):
            st.image(cm_img, caption="Classification Confusion Matrix", use_container_width=True)


# =============================================================================
# TAB: BATCH STUDENT PREDICTION
# =============================================================================
with tabs[tab_offset + 7]:
    st.subheader("Bulk Student Performance Prediction")
    st.write("Upload a CSV containing multiple student records to evaluate entire cohorts simultaneously.")
    
    sample_df = pd.DataFrame([
        {
            "Student_ID": "STU9001", "Age": 20, "Gender": "Female",
            "Parental_Education": "Bachelor", "Study_Hours_Per_Week": 16.0,
            "Attendance_Rate": 85.0, "Past_Exam_Score": 75.0,
            "Internal_Assessment_Score": 38.0, "Assignment_Completion_Rate": 90.0,
            "Tutoring_Classes": "Yes", "Internet_Access": "Yes",
            "Extracurricular_Activities": "No", "Sleep_Hours_Per_Day": 7.5
        },
        {
            "Student_ID": "STU9002", "Age": 21, "Gender": "Male",
            "Parental_Education": "High School", "Study_Hours_Per_Week": 5.0,
            "Attendance_Rate": 52.0, "Past_Exam_Score": 42.0,
            "Internal_Assessment_Score": 18.0, "Assignment_Completion_Rate": 55.0,
            "Tutoring_Classes": "No", "Internet_Access": "Yes",
            "Extracurricular_Activities": "Yes", "Sleep_Hours_Per_Day": 5.0
        }
    ])
    
    csv_sample = sample_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Sample Batch CSV Template",
        data=csv_sample,
        file_name="student_prediction_sample_template.csv",
        mime="text/csv"
    )
    
    uploaded_file = st.file_uploader("Upload CSV File for Prediction", type=["csv"])
    if uploaded_file is not None and loaded:
        try:
            batch_df = pd.read_csv(uploaded_file)
            st.write(f"Loaded **{len(batch_df)}** records for evaluation:")
            st.dataframe(batch_df.head(), use_container_width=True)
            
            batch_proc = batch_df.copy()
            cat_cols = ["Gender", "Parental_Education", "Tutoring_Classes", "Internet_Access", "Extracurricular_Activities"]
            for col in cat_cols:
                batch_proc[col] = encoders[col].transform(batch_proc[col])
                
            features = meta["features"]
            X_batch = batch_proc[features]
            
            preds_c = clf.predict(X_batch)
            preds_r = np.round(np.clip(reg.predict(X_batch), 0, 100), 1)
            
            results_df = batch_df.copy()
            results_df["Predicted_Tier"] = preds_c
            results_df["Predicted_Final_Score"] = preds_r
            results_df["Predicted_Pass"] = np.where(preds_r >= 50.0, "Yes", "No")
            
            st.success("Predictions generated successfully!")
            st.dataframe(results_df, use_container_width=True)
            
            res_csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Full Predictions CSV",
                data=res_csv,
                file_name="batch_student_predictions_output.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error processing file: {e}. Please ensure column names match the template.")


# =============================================================================
# TAB: POWER BI INTEGRATION
# =============================================================================
with tabs[tab_offset + 8]:
    st.subheader("Power BI Business Intelligence Kit")
    st.markdown("""
    This project integrates with **Microsoft Power BI** to enable university administrators, department heads,
    and academic coordinators to explore multidimensional performance dashboards.
    """)
    
    pbi_col1, pbi_col2 = st.columns([1, 1])
    
    with pbi_col1:
        st.markdown("#### 📦 Ready-to-Use Power BI Artifacts")
        st.markdown("""
        The project includes:
        - **Curated Dataset**: `data/student_performance_powerbi.csv` with calculated risk flags and attendance cohorts.
        - **Custom Power BI Theme**: `powerbi/powerbi_theme.json` for styling.
        - **DAX Measures Repository**: `powerbi/dax_measures.txt` containing 15+ ready formulas.
        - **Dashboard Manual**: `powerbi/POWERBI_DASHBOARD_GUIDE.md` with page-by-page layout tutorials.
        """)
        
        pbi_csv_path = "data/student_performance_powerbi.csv"
        if os.path.exists(pbi_csv_path):
            with open(pbi_csv_path, "rb") as f:
                st.download_button(
                    label="📥 Download Power BI Prepared Dataset (CSV)",
                    data=f,
                    file_name="student_performance_powerbi.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
    with pbi_col2:
        st.markdown("#### 📐 Key DAX Measures Preview")
        st.code("""
-- Pass Rate %
Pass Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS('student_performance_powerbi'), 'student_performance_powerbi'[Passed] = "Yes"),
    COUNTROWS('student_performance_powerbi'),
    0
) * 100

-- High Risk Alert Count
High Risk Students = 
CALCULATE(
    COUNTROWS('student_performance_powerbi'),
    'student_performance_powerbi'[Risk_Level] = "High Risk"
)
        """, language="sql")
        
    st.divider()
    st.markdown("#### 📋 Power BI Dataset Preview")
    if os.path.exists(pbi_csv_path):
        preview_df = pd.read_csv(pbi_csv_path)
        st.dataframe(preview_df.head(10), use_container_width=True)
