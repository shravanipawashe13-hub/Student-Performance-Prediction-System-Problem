"""
Data Generation, Cleaning, and Preprocessing Module
Student Performance Prediction System (BCA Project)
"""

import os
import numpy as np
import pandas as pd

def generate_student_dataset(n_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic student academic and demographic dataset
    with realistic correlations to final academic performance.
    """
    np.random.seed(random_state)
    
    student_ids = [f"STU{1000 + i}" for i in range(1, n_samples + 1)]
    ages = np.random.choice([18, 19, 20, 21, 22, 23], size=n_samples, p=[0.25, 0.35, 0.22, 0.12, 0.04, 0.02])
    genders = np.random.choice(["Male", "Female"], size=n_samples, p=[0.52, 0.48])
    
    # Study Habits & Attendance
    study_hours = np.round(np.random.gamma(shape=4.0, scale=3.5, size=n_samples), 1)
    study_hours = np.clip(study_hours, 2.0, 35.0)
    
    attendance = np.round(np.random.beta(a=7, b=2, size=n_samples) * 100, 1)
    attendance = np.clip(attendance, 40.0, 100.0)
    
    past_exam_score = np.round(np.random.normal(loc=65, scale=14, size=n_samples), 1)
    past_exam_score = np.clip(past_exam_score, 30.0, 98.0)
    
    internal_assessment = np.round(past_exam_score * 0.45 + np.random.normal(0, 3.5, size=n_samples), 1)
    internal_assessment = np.clip(internal_assessment, 12.0, 50.0)
    
    assignment_completion = np.round(attendance * 0.7 + np.random.uniform(10, 30, size=n_samples), 1)
    assignment_completion = np.clip(assignment_completion, 45.0, 100.0)
    
    tutoring = np.random.choice(["Yes", "No"], size=n_samples, p=[0.38, 0.62])
    internet_access = np.random.choice(["Yes", "No"], size=n_samples, p=[0.88, 0.12])
    extracurricular = np.random.choice(["Yes", "No"], size=n_samples, p=[0.45, 0.55])
    
    sleep_hours = np.round(np.random.normal(loc=7.0, scale=1.1, size=n_samples), 1)
    sleep_hours = np.clip(sleep_hours, 4.0, 10.0)
    
    parental_edu = np.random.choice(
        ["High School", "Diploma", "Bachelor", "Master"],
        size=n_samples,
        p=[0.28, 0.24, 0.36, 0.12]
    )
    
    # Calculate Final Score using weighted realistic relationship
    base_score = (
        0.28 * past_exam_score +
        0.26 * (internal_assessment * 2.0) +
        0.20 * attendance +
        0.14 * (study_hours * 2.5) +
        0.08 * assignment_completion
    )
    
    # Additional positive/negative behavioral factors
    tutoring_bonus = np.where(tutoring == "Yes", 3.5, 0.0)
    internet_bonus = np.where(internet_access == "Yes", 2.0, -2.5)
    sleep_penalty = np.where((sleep_hours < 5.5) | (sleep_hours > 9.0), -3.0, 1.5)
    parental_bonus = np.select(
        [parental_edu == "Master", parental_edu == "Bachelor", parental_edu == "Diploma"],
        [2.5, 1.5, 0.5],
        default=0.0
    )
    
    noise = np.random.normal(0, 3.0, size=n_samples)
    final_score = np.round(base_score + tutoring_bonus + internet_bonus + sleep_penalty + parental_bonus + noise, 1)
    final_score = np.clip(final_score, 25.0, 99.5)
    
    # Categorical Performance Tier
    conditions = [
        final_score >= 80.0,
        (final_score >= 65.0) & (final_score < 80.0),
        (final_score >= 50.0) & (final_score < 65.0),
        final_score < 50.0
    ]
    tiers = ["Distinction", "Merit", "Pass", "At-Risk"]
    performance_tier = np.select(conditions, tiers, default="Pass")
    passed = np.where(final_score >= 50.0, "Yes", "No")
    
    df = pd.DataFrame({
        "Student_ID": student_ids,
        "Age": ages,
        "Gender": genders,
        "Parental_Education": parental_edu,
        "Study_Hours_Per_Week": study_hours,
        "Attendance_Rate": attendance,
        "Past_Exam_Score": past_exam_score,
        "Internal_Assessment_Score": internal_assessment,
        "Assignment_Completion_Rate": assignment_completion,
        "Tutoring_Classes": tutoring,
        "Internet_Access": internet_access,
        "Extracurricular_Activities": extracurricular,
        "Sleep_Hours_Per_Day": sleep_hours,
        "Final_Score": final_score,
        "Performance_Category": performance_tier,
        "Passed": passed
    })
    
    return df


def prepare_powerbi_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches dataset with extra attributes useful for Power BI slicing & drilldowns:
    - Attendance Group (<65%, 65-75%, 75-85%, >85%)
    - Study Time Group (Low, Moderate, High)
    - Risk Level (High, Medium, Low)
    - Grade Points (BCA GPA scale 0-10)
    """
    pbi_df = df.copy()
    
    # Attendance Groups
    pbi_df["Attendance_Group"] = pd.cut(
        pbi_df["Attendance_Rate"],
        bins=[0, 65, 75, 85, 100],
        labels=["Critical (<65%)", "Moderate (65-75%)", "Good (75-85%)", "Excellent (>85%)"]
    )
    
    # Study Time Groups
    pbi_df["Study_Hours_Group"] = pd.cut(
        pbi_df["Study_Hours_Per_Week"],
        bins=[0, 8, 16, 40],
        labels=["Low (<8 hrs)", "Medium (8-16 hrs)", "High (>16 hrs)"]
    )
    
    # Risk Level
    pbi_df["Risk_Level"] = np.select(
        [
            (pbi_df["Final_Score"] < 50) | (pbi_df["Attendance_Rate"] < 60),
            (pbi_df["Final_Score"] >= 50) & (pbi_df["Final_Score"] < 65),
            pbi_df["Final_Score"] >= 65
        ],
        ["High Risk", "Moderate Risk", "Low Risk"],
        default="Moderate Risk"
    )
    
    # GPA Equivalent (10 point scale)
    pbi_df["Grade_Point"] = np.round(np.clip(pbi_df["Final_Score"] / 10.0, 0, 10.0), 2)
    
    return pbi_df


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save_all_datasets(data_dir: str = None):
    """
    Generates and saves:
    1. student_performance_raw.csv
    2. student_performance_cleaned.csv
    3. student_performance_powerbi.csv
    """
    if data_dir is None:
        data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print("Generating synthetic student performance dataset...")
    df = generate_student_dataset(n_samples=1200, random_state=42)
    
    # Save raw
    raw_path = os.path.join(data_dir, "student_performance_raw.csv")
    df.to_csv(raw_path, index=False)
    print(f"Saved raw dataset to: {raw_path}")
    
    # Preprocessing / Cleaning steps (standard check, no missing values in this synthesized set)
    cleaned_df = df.dropna().drop_duplicates()
    cleaned_path = os.path.join(data_dir, "student_performance_cleaned.csv")
    cleaned_df.to_csv(cleaned_path, index=False)
    print(f"Saved cleaned dataset to: {cleaned_path}")
    
    # Power BI Enriched
    pbi_df = prepare_powerbi_dataset(cleaned_df)
    pbi_path = os.path.join(data_dir, "student_performance_powerbi.csv")
    pbi_df.to_csv(pbi_path, index=False)
    print(f"Saved Power BI dataset to: {pbi_path}")
    
    print(f"Dataset summary:\n- Total records: {len(df)}")
    print(f"- Features: {list(df.columns)}")
    print(f"- Performance Tier Breakdown:\n{df['Performance_Category'].value_counts()}")


if __name__ == "__main__":
    save_all_datasets()
