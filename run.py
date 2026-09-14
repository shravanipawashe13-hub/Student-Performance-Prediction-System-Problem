"""
================================================================================
🎓 Student Performance Prediction & Academic Analytics System
Universal Cross-Platform Master Launcher (run.py)
================================================================================
Works on ANY PC (Windows, macOS, Linux).
Usage:
    python run.py

This script will:
1. Detect and validate your Python environment.
2. Check and automatically install missing requirements from requirements.txt.
3. Automatically generate synthetic datasets, EDA charts, and train ML models if not found.
4. Initialize the SQL database (SQLite/MySQL) and user accounts.
5. Launch the Streamlit interactive web application and open it in your browser.
================================================================================
"""

import sys
import os
import subprocess
import platform

# Ensure working directory is always the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)


def log(prefix: str, message: str):
    symbols = {
        "INFO": "[*]",
        "OK": "[+]",
        "WARN": "[!]",
        "ERR": "[-]",
        "STEP": "[>]"
    }
    sym = symbols.get(prefix, "[*]")
    print(f"{sym} [{prefix}] {message}")


def find_best_python():
    """Finds the best Python executable on the current system."""
    if (3, 8) <= sys.version_info < (3, 14):
        return sys.executable

    if sys.platform.startswith("win"):
        # Windows py launcher check
        for ver in ["-3.12", "-3.11", "-3.13", "-3.10", "-3"]:
            try:
                out = subprocess.check_output(
                    ["py", ver, "-c", "import sys; print(sys.executable)"],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if out and os.path.exists(out):
                    return out
            except Exception:
                pass

        # Standard Windows install paths
        local_app = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        candidate_dirs = [
            os.path.join(local_app, "Programs", "Python"),
            prog_files,
            "C:\\"
        ]
        for base in candidate_dirs:
            if os.path.exists(base):
                for py_folder in ["Python312", "Python311", "Python313", "Python310"]:
                    exe = os.path.join(base, py_folder, "python.exe")
                    if os.path.exists(exe):
                        return exe

    return sys.executable


def check_and_install_dependencies(py_exe: str):
    """Verifies and installs required dependencies."""
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "scikit-learn",
        "seaborn",
        "matplotlib",
        "plotly",
        "openpyxl"
    ]
    
    missing = []
    for pkg in required_packages:
        check_mod = pkg.replace("-", "_")
        try:
            subprocess.check_call(
                [py_exe, "-c", f"import {check_mod}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            missing.append(pkg)
            
    if missing:
        log("WARN", f"Missing packages detected: {', '.join(missing)}")
        log("STEP", "Installing requirements from requirements.txt via pip...")
        req_file = os.path.join(PROJECT_ROOT, "requirements.txt")
        if os.path.exists(req_file):
            cmd = [py_exe, "-m", "pip", "install", "-r", req_file]
        else:
            cmd = [py_exe, "-m", "pip", "install"] + missing
            
        res = subprocess.run(cmd)
        if res.returncode != 0:
            log("WARN", "Pip installation encountered warnings. Attempting to continue...")
        else:
            log("OK", "All required dependencies installed successfully.")
    else:
        log("OK", "All required Python libraries are already installed.")


def bootstrap_project_artifacts(py_exe: str):
    """Generates synthetic data, EDA visualizations, models, and DB if missing."""
    data_file = os.path.join(PROJECT_ROOT, "data", "student_performance_cleaned.csv")
    model_file = os.path.join(PROJECT_ROOT, "models", "decision_tree_classifier.pkl")
    vis_file = os.path.join(PROJECT_ROOT, "visualizations", "correlation_heatmap.png")

    if not os.path.exists(data_file):
        log("STEP", "Step 1/3: Generating synthetic student dataset...")
        subprocess.run([py_exe, os.path.join(PROJECT_ROOT, "src", "data_prep.py")])

    if not os.path.exists(vis_file):
        log("STEP", "Step 2/3: Generating Exploratory Data Analysis (EDA) visualizations...")
        subprocess.run([py_exe, os.path.join(PROJECT_ROOT, "src", "eda.py")])

    if not os.path.exists(model_file):
        log("STEP", "Step 3/3: Training and persisting Decision Tree ML models...")
        subprocess.run([py_exe, os.path.join(PROJECT_ROOT, "src", "train.py")])

    # Initialize SQL DB and default credentials
    try:
        import src.tracker as tracker
        import src.auth as auth
        auth.init_auth_table()
        auth.sync_students_with_users()
        tracker.init_tracker_data()
        log("OK", "SQL database tables & RBAC user accounts initialized.")
    except Exception as e:
        log("WARN", f"Database init note: {e}")


def launch_application(py_exe: str):
    """Launches the Streamlit application."""
    app_path = os.path.join(PROJECT_ROOT, "app.py")
    log("STEP", "Launching Student Performance Prediction System (Streamlit)...")
    print("\n" + "=" * 70)
    print("Web Application will open at: http://localhost:8501")
    print("Default Login Credentials:")
    print("   Admin:   admin   / admin123")
    print("   Teacher: teacher / teacher123")
    print("   Student: student / student123 (or select student from dropdown)")
    print("Press Ctrl+C in this terminal to stop the application.")
    print("=" * 70 + "\n")

    env = os.environ.copy()
    env["STREAMLIT_AUTO_LAUNCHED"] = "1"
    
    cmd = [
        py_exe, "-m", "streamlit", "run", app_path,
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]
    subprocess.run(cmd, env=env)


def main():
    print("\n" + "=" * 70)
    print("STUDENT PERFORMANCE PREDICTION & ACADEMIC ANALYTICS SYSTEM")
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print("=" * 70)

    py_exe = find_best_python()
    log("INFO", f"Active Python interpreter: {py_exe}")
    
    check_and_install_dependencies(py_exe)
    bootstrap_project_artifacts(py_exe)
    launch_application(py_exe)


if __name__ == "__main__":
    main()
