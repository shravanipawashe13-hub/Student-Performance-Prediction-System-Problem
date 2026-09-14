"""
Exploratory Data Analysis (EDA) Module
Student Performance Prediction System (BCA Project)
Utilizes Seaborn and Matplotlib for publication-quality visualizations.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for script execution
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic visual themes
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300
})


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_eda(data_path: str = None, output_dir: str = None):
    """
    Executes full EDA pipeline and exports all Seaborn visualizations.
    """
    if data_path is None:
        data_path = os.path.join(BASE_DIR, "data", "student_performance_cleaned.csv")
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "visualizations")
        
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file {data_path} not found. Please run data_prep.py first.")
    
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(data_path)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # 1. Correlation Heatmap
    print("Generating: 1. Correlation Heatmap...")
    numeric_cols = [
        "Age", "Study_Hours_Per_Week", "Attendance_Rate",
        "Past_Exam_Score", "Internal_Assessment_Score",
        "Assignment_Completion_Rate", "Sleep_Hours_Per_Day", "Final_Score"
    ]
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 7))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-0.2,
        center=0,
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=1.0,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation"}
    )
    plt.title("Correlation Analysis of Academic & Lifestyle Factors", pad=15, fontweight="bold")
    plt.tight_layout()
    corr_img_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(corr_img_path)
    plt.close()
    
    # 2. Attendance vs Final Score with Regression Line
    print("Generating: 2. Attendance vs Final Score...")
    plt.figure(figsize=(9, 6))
    palette = {"Distinction": "#1f77b4", "Merit": "#2ca02c", "Pass": "#ff7f0e", "At-Risk": "#d62728"}
    
    sns.scatterplot(
        data=df,
        x="Attendance_Rate",
        y="Final_Score",
        hue="Performance_Category",
        palette=palette,
        alpha=0.75,
        s=60,
        edgecolor="w"
    )
    sns.regplot(
        data=df,
        x="Attendance_Rate",
        y="Final_Score",
        scatter=False,
        color="#2b2b2b",
        line_kws={"linestyle": "--", "linewidth": 2, "label": "Trend Line"}
    )
    # Threshold lines
    plt.axvline(x=75, color="gray", linestyle=":", label="75% Attendance Requirement")
    plt.axhline(y=50, color="red", linestyle=":", label="Pass Threshold (50%)")
    
    plt.title("Impact of Attendance Rate on Final Examination Score", pad=12, fontweight="bold")
    plt.xlabel("Attendance Rate (%)")
    plt.ylabel("Final Exam Score (out of 100)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "attendance_vs_performance.png"))
    plt.close()
    
    # 3. Study Hours Distribution & KDE by Pass/Fail
    print("Generating: 3. Study Hours Distribution...")
    plt.figure(figsize=(9, 5.5))
    sns.histplot(
        data=df,
        x="Study_Hours_Per_Week",
        hue="Passed",
        kde=True,
        bins=25,
        palette={"Yes": "#2ca02c", "No": "#d62728"},
        alpha=0.5,
        element="step"
    )
    plt.title("Weekly Study Hours Distribution: Passed vs At-Risk Students", pad=12, fontweight="bold")
    plt.xlabel("Weekly Study Hours (hrs/week)")
    plt.ylabel("Student Count")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "study_hours_distribution.png"))
    plt.close()
    
    # 4. Final Score by Parental Education & Tutoring
    print("Generating: 4. Final Score by Parental Education & Tutoring...")
    plt.figure(figsize=(10, 6))
    order = ["High School", "Diploma", "Bachelor", "Master"]
    sns.boxplot(
        data=df,
        x="Parental_Education",
        y="Final_Score",
        hue="Tutoring_Classes",
        order=order,
        palette="Set2",
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"}
    )
    plt.title("Academic Performance by Parental Education Level and Tutoring Support", pad=12, fontweight="bold")
    plt.xlabel("Parental Education Level")
    plt.ylabel("Final Score (%)")
    plt.legend(title="Attended Tutoring", loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grade_distribution_by_parental_edu.png"))
    plt.close()
    
    # 5. Performance Category Breakdown
    print("Generating: 5. Performance Category Breakdown...")
    plt.figure(figsize=(8, 5))
    order_cat = ["Distinction", "Merit", "Pass", "At-Risk"]
    palette_cat = ["#2b5c8f", "#3caea3", "#f6d55c", "#ed553b"]
    
    ax = sns.countplot(
        data=df,
        x="Performance_Category",
        order=order_cat,
        hue="Performance_Category",
        palette=palette_cat,
        legend=False
    )
    total = len(df)
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f"{int(height)} ({height/total*100:.1f}%)",
            (p.get_x() + p.get_width() / 2., height + 8),
            ha="center", va="bottom", fontsize=10, fontweight="bold"
        )
    
    plt.title("Distribution of Student Performance Tiers", pad=12, fontweight="bold")
    plt.xlabel("Performance Tier")
    plt.ylabel("Number of Students")
    plt.ylim(0, max([p.get_height() for p in ax.patches]) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "performance_category_breakdown.png"))
    plt.close()
    
    # 6. Sleep Hours vs Performance Curve
    print("Generating: 6. Sleep Hours vs Performance Curve...")
    plt.figure(figsize=(9, 5.5))
    sns.lineplot(
        data=df,
        x="Sleep_Hours_Per_Day",
        y="Final_Score",
        estimator="mean",
        errorbar=("ci", 95),
        color="#7b2cbf",
        linewidth=2.5,
        marker="o"
    )
    plt.axvspan(6.5, 8.5, color="#52b788", alpha=0.2, label="Optimal Sleep Window (6.5 - 8.5 hrs)")
    plt.title("Impact of Daily Sleep Duration on Student Performance", pad=12, fontweight="bold")
    plt.xlabel("Average Sleep Duration (Hours/Day)")
    plt.ylabel("Mean Final Exam Score (%)")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sleep_vs_performance.png"))
    plt.close()
    
    print(f"All 6 Seaborn visualizations successfully exported to '{output_dir}/'")


if __name__ == "__main__":
    run_eda()
