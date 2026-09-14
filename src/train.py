"""
Machine Learning Training Module: Decision Trees
Student Performance Prediction System (BCA Project)
Trains both Decision Tree Classifier (Grade/Risk) and Decision Tree Regressor (Final Score).
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
    mean_absolute_error, root_mean_squared_error, r2_score
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def train_decision_tree_models(
    data_path: str = None,
    model_dir: str = None,
    vis_dir: str = None
):
    """
    Trains, evaluates, and persists Decision Tree models.
    """
    if data_path is None:
        data_path = os.path.join(BASE_DIR, "data", "student_performance_cleaned.csv")
    if model_dir is None:
        model_dir = os.path.join(BASE_DIR, "models")
    if vis_dir is None:
        vis_dir = os.path.join(BASE_DIR, "visualizations")

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(vis_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    print(f"Loaded dataset for training: {df.shape}")
    
    # Feature Selection
    feature_cols = [
        "Age", "Gender", "Parental_Education", "Study_Hours_Per_Week",
        "Attendance_Rate", "Past_Exam_Score", "Internal_Assessment_Score",
        "Assignment_Completion_Rate", "Tutoring_Classes", "Internet_Access",
        "Extracurricular_Activities", "Sleep_Hours_Per_Day"
    ]
    
    X = df[feature_cols].copy()
    y_class = df["Performance_Category"].copy()
    y_reg = df["Final_Score"].copy()
    
    # Encode Categorical Variables
    encoders = {}
    cat_cols = ["Gender", "Parental_Education", "Tutoring_Classes", "Internet_Access", "Extracurricular_Activities"]
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
    
    # Save encoders for live inference
    encoders_path = os.path.join(model_dir, "encoders.pkl")
    with open(encoders_path, "wb") as f:
        pickle.dump(encoders, f)
    print(f"Saved feature encoders to: {encoders_path}")
    
    # Stratified Train-Test Split for classification
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    
    # Train-Test Split for regression
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )
    
    # =========================================================================
    # 1. DECISION TREE CLASSIFIER (Predicting Performance Tier)
    # =========================================================================
    print("\nTraining Decision Tree Classifier...")
    # Using balanced depth to avoid overfitting while retaining interpretability
    clf = DecisionTreeClassifier(
        criterion="entropy",
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    clf.fit(X_train_c, y_train_c)
    
    y_pred_c = clf.predict(X_test_c)
    acc = accuracy_score(y_test_c, y_pred_c)
    prec = precision_score(y_test_c, y_pred_c, average="weighted")
    rec = recall_score(y_test_c, y_pred_c, average="weighted")
    f1 = f1_score(y_test_c, y_pred_c, average="weighted")
    
    print(f"Classifier Accuracy: {acc * 100:.2f}%")
    print(f"Precision (Weighted): {prec:.4f}")
    print(f"Recall (Weighted):    {rec:.4f}")
    print(f"F1-Score (Weighted):  {f1:.4f}")
    print("\nClassification Report:\n", classification_report(y_test_c, y_pred_c))
    
    # Save Classifier Model
    clf_path = os.path.join(model_dir, "decision_tree_classifier.pkl")
    with open(clf_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"Saved Classifier to: {clf_path}")
    
    # Generate Confusion Matrix Visualization
    labels = ["Distinction", "Merit", "Pass", "At-Risk"]
    cm = confusion_matrix(y_test_c, y_pred_c, labels=labels)
    
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        cbar=False,
        annot_kws={"size": 12, "weight": "bold"}
    )
    plt.title("Decision Tree Confusion Matrix (Student Tiers)", pad=12, fontweight="bold")
    plt.xlabel("Predicted Tier", fontweight="bold")
    plt.ylabel("Actual Tier", fontweight="bold")
    plt.tight_layout()
    cm_path = os.path.join(vis_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Saved confusion matrix plot to: {cm_path}")
    
    # =========================================================================
    # 2. DECISION TREE REGRESSOR (Predicting Exact Final Score 0-100)
    # =========================================================================
    print("\nTraining Decision Tree Regressor...")
    reg = DecisionTreeRegressor(
        criterion="squared_error",
        max_depth=6,
        min_samples_split=12,
        min_samples_leaf=6,
        random_state=42
    )
    reg.fit(X_train_r, y_train_r)
    
    y_pred_r = reg.predict(X_test_r)
    mae = mean_absolute_error(y_test_r, y_pred_r)
    rmse = root_mean_squared_error(y_test_r, y_pred_r)
    r2 = r2_score(y_test_r, y_pred_r)
    
    print(f"Regressor MAE:  {mae:.2f} marks")
    print(f"Regressor RMSE: {rmse:.2f} marks")
    print(f"Regressor R²:   {r2:.4f}")
    
    # Save Regressor Model
    reg_path = os.path.join(model_dir, "decision_tree_regressor.pkl")
    with open(reg_path, "wb") as f:
        pickle.dump(reg, f)
    print(f"Saved Regressor to: {reg_path}")
    
    # =========================================================================
    # 3. FEATURE IMPORTANCE VISUALIZATION (Seaborn Barplot)
    # =========================================================================
    importances = clf.feature_importances_
    feat_df = pd.DataFrame({
        "Feature": [c.replace("_", " ") for c in feature_cols],
        "Importance": importances
    }).sort_values("Importance", ascending=False)
    
    plt.figure(figsize=(9, 5.5))
    sns.barplot(
        data=feat_df,
        x="Importance",
        y="Feature",
        palette="viridis",
        hue="Feature",
        legend=False
    )
    for idx, row in enumerate(feat_df.itertuples()):
        plt.text(row.Importance + 0.005, idx, f"{row.Importance*100:.1f}%", va="center", fontsize=9, fontweight="bold")
    
    plt.title("Decision Tree Feature Importance in Predicting Performance", pad=12, fontweight="bold")
    plt.xlabel("Importance Weight (Normalized)")
    plt.xlim(0, max(feat_df["Importance"]) * 1.18)
    plt.tight_layout()
    feat_path = os.path.join(vis_dir, "feature_importance.png")
    plt.savefig(feat_path, dpi=300)
    plt.close()
    print(f"Saved feature importance plot to: {feat_path}")
    
    # =========================================================================
    # 4. DECISION TREE VISUAL DIAGRAM EXPORT
    # =========================================================================
    print("Exporting Decision Tree visual graph diagram...")
    plt.figure(figsize=(24, 12), dpi=300)
    plot_tree(
        clf,
        feature_names=[c.replace("_", " ") for c in feature_cols],
        class_names=clf.classes_,
        filled=True,
        rounded=True,
        fontsize=8,
        max_depth=3  # Visually legible representation of top 3 levels
    )
    plt.title("Decision Tree Structure Diagram (Top Levels)", fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()
    tree_path = os.path.join(vis_dir, "decision_tree_structure.png")
    plt.savefig(tree_path, bbox_inches="tight")
    plt.close()
    print(f"Saved decision tree structure to: {tree_path}")
    
    # =========================================================================
    # 5. METADATA EXPORT
    # =========================================================================
    metadata = {
        "features": feature_cols,
        "categorical_features": cat_cols,
        "target_classes": list(clf.classes_),
        "classifier_metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4)
        },
        "regressor_metrics": {
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "r2_score": round(float(r2), 4)
        },
        "feature_importances": dict(zip(feature_cols, [round(float(x), 4) for x in importances]))
    }
    
    meta_path = os.path.join(model_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Saved model metadata to: {meta_path}")
    
    print("\nModel training and artifact generation completed successfully!")
    return metadata


if __name__ == "__main__":
    train_decision_tree_models()
