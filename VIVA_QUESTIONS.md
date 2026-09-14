# Viva-Voce Preparation Guide & Frequently Asked Questions (FAQ)
## Student Performance Prediction System (BCA Project)

This guide contains **25+ key technical questions and structured answers** commonly asked by external college examiners during BCA project viva examinations.

---

### Section 1: Project Concept & System Architecture

#### Q1: What is the main objective of your project?
**Answer:**  
The objective is to predict student final examination performance (both tier classification—*Distinction, Merit, Pass, At-Risk*—and exact percentage marks) before end-term exams take place. This allows faculties to identify struggling students early and implement targeted academic interventions (extra classes, study counseling) before the student fails.

#### Q2: What are the key technologies and libraries used in this project?
**Answer:**  
- **Python**: Core programming language.
- **Pandas & NumPy**: Data ingestion, manipulation, missing value cleaning, and feature engineering.
- **Seaborn & Matplotlib**: Statistical data visualization and exploratory data analysis (EDA).
- **Scikit-Learn**: Machine learning library used for Decision Tree Classification and Regression.
- **Streamlit**: Interactive web user interface for real-time inference and batch CSV evaluation.
- **Microsoft Power BI**: Business intelligence reporting tool with DAX measures for executive-level institutional analytics.

#### Q3: What features (inputs) does your model use to make predictions?
**Answer:**  
The model utilizes 12 features across three categories:
1. **Academic indicators**: Previous Semester Exam Score, Internal Assessment Marks, Attendance Rate (%), and Assignment Completion Rate (%).
2. **Behavioral & Lifestyle habits**: Weekly Study Hours, Average Daily Sleep Hours, Tutoring Support, and Extracurricular Participation.
3. **Demographic & Environmental**: Student Age, Gender, Parental Education Level, and Home Internet Connectivity.

---

### Section 2: Machine Learning & Decision Trees

#### Q4: Why did you choose Decision Trees over other machine learning algorithms?
**Answer:**  
1. **Interpretability & Explainability**: In an academic environment, black-box models (like neural networks) cannot explain *why* a student is predicted to fail. A Decision Tree generates transparent, human-readable if-else rules (e.g., `IF Attendance < 65% AND Internal < 25 THEN At-Risk`).
2. **Handles Non-Linear Relationships**: Academic parameters do not always have purely linear relationships (e.g., sleep duration has an optimal middle range, rather than higher-is-always-better).
3. **No Stringent Scaling Required**: Unlike KNN or SVM which depend on Euclidean distance, Decision Trees are invariant to feature scale differences.

#### Q5: What is the difference between Gini Impurity and Entropy in Decision Trees?
**Answer:**  
Both are metrics used to measure the impurity or disorder of a node:
- **Entropy** measures information disorder: $\text{Entropy}(S) = -\sum p_i \log_2(p_i)$. It ranges from 0 to 1 and involves logarithmic calculation.
- **Gini Impurity** measures the probability of a randomly chosen element being incorrectly classified: $\text{Gini}(S) = 1 - \sum p_i^2$. It ranges from 0 to 0.5 and is computationally faster because it does not compute logarithms.
In our classifier, we used `criterion='entropy'` to maximize Information Gain.

#### Q6: What is overfitting in Decision Trees and how did you prevent it?
**Answer:**  
Overfitting occurs when a Decision Tree grows too deep, memorizing noise and specific outliers in the training set instead of learning generalizable patterns. When overfitted, training accuracy is close to 100%, but testing accuracy drops sharply.
We prevented overfitting using **pre-pruning hyperparameters**:
- `max_depth = 5`: Capped tree depth to 5 levels.
- `min_samples_split = 10`: A node must have at least 10 samples to split.
- `min_samples_leaf = 5`: Every terminal leaf must contain at least 5 students.

#### Q7: How does a Decision Tree Regressor differ from a Decision Tree Classifier?
**Answer:**  
- A **Decision Tree Classifier** predicts discrete category labels (*Distinction, Merit, Pass, At-Risk*) and splits nodes to maximize information gain or minimize Gini/Entropy. The leaf prediction is the majority class.
- A **Decision Tree Regressor** predicts continuous numerical values (*marks 0–100*) and splits nodes to minimize Mean Squared Error (MSE) or Mean Absolute Error (MAE). The leaf prediction is the mathematical mean of the target values in that leaf.

#### Q8: What evaluation metrics did you use for classification and regression?
**Answer:**  
- **For Classification**:
  - **Accuracy**: Overall fraction of correct predictions ($\approx 74.2\%$).
  - **Precision**: Proportion of predicted positives that were truly positive.
  - **Recall**: Proportion of actual positives correctly identified by the model.
  - **F1-Score**: Harmonic mean of Precision and Recall.
  - **Confusion Matrix**: 4x4 matrix mapping actual vs predicted categories.
- **For Regression**:
  - **Mean Absolute Error (MAE)**: Average magnitude of prediction error ($\approx 3.98$ marks).
  - **Root Mean Squared Error (RMSE)**: Penalizes larger deviations ($\approx 4.97$ marks).
  - **R-Squared ($R^2$)**: Proportion of variance in marks explained by the model ($\approx 0.706$).

---

### Section 3: Data Science with Pandas, Seaborn & Matplotlib

#### Q9: What is the purpose of the Pandas library in your system?
**Answer:**  
Pandas provides high-performance data structures (DataFrames and Series). We utilized Pandas for:
- Reading raw CSV files via `pd.read_csv()`.
- Missing value verification using `.isna().sum()`.
- Data binning into cohorts using `pd.cut()`.
- Groupby aggregations and summary statistics with `.describe()`.
- Exporting processed datasets via `.to_csv()`.

#### Q10: Why did you use Seaborn instead of just basic Matplotlib?
**Answer:**  
Seaborn is built on top of Matplotlib and integrates directly with Pandas DataFrames:
- Provides high-level statistical plotting functions like `sns.heatmap()`, `sns.kdeplot()`, `sns.boxplot()`, and `sns.regplot()` with built-in trend estimation and confidence intervals.
- Offers modern color palettes and aesthetics with concise code compared to Matplotlib.

#### Q11: What key insight did your Correlation Heatmap reveal?
**Answer:**  
The correlation heatmap showed that **Past Exam Score** ($r \approx 0.85$) and **Internal Assessment Score** ($r \approx 0.82$) have the strongest positive correlation with final grades, followed closely by **Attendance Rate** ($r \approx 0.64$). Factors like age and gender exhibited near-zero correlation ($r < 0.05$), proving that demographic variables do not bias academic performance.

#### Q12: What non-linear relationship did you discover during EDA?
**Answer:**  
The relationship between **Daily Sleep Hours** and **Final Exam Score** was non-linear:
- Students sleeping less than 6 hours had lower scores due to cognitive fatigue.
- Students sleeping between **6.5 and 8.5 hours** scored the highest marks.
- Students sleeping more than 9 hours showed reduced scores, often correlated with low study hours.

---

### Section 4: Power BI & Business Intelligence

#### Q13: What role does Microsoft Power BI play in this project?
**Answer:**  
While Python and Scikit-Learn perform the data science modeling and predictive computation, Power BI serves as the **Executive Business Intelligence Dashboard** for college administrators, HODs, and mentors. It allows non-technical stakeholders to interactively slice data by department, gender, attendance thresholds, and inspect early-warning rosters.

#### Q14: What is DAX in Power BI? Name two DAX measures you wrote.
**Answer:**  
**DAX (Data Analysis Expressions)** is the formula language used in Power BI for custom calculations, aggregations, and business logic.
Two measures we developed:
1. `Pass Rate % = DIVIDE(CALCULATE(COUNTROWS('student_performance_powerbi'), 'student_performance_powerbi'[Passed] = "Yes"), COUNTROWS('student_performance_powerbi'), 0) * 100`
2. `High Risk Students = CALCULATE(COUNTROWS('student_performance_powerbi'), 'student_performance_powerbi'[Risk_Level] = "High Risk")`

#### Q15: What is the difference between a Calculated Column and a Measure in Power BI?
**Answer:**  
- A **Calculated Column** is computed row-by-row during data refresh and stored in memory in the table model (e.g., `Risk_Level`).
- A **Measure** is calculated dynamically on-the-fly depending on user slicers and filters active in the visual (e.g., `Average Final Score` or `Pass Rate %`). Measures consume less RAM and are best practice for aggregations.

---

### Section 5: Web Application & Deployment

#### Q16: How does the Streamlit web application work?
**Answer:**  
Streamlit creates a reactive web application directly from Python. When a user changes an input slider (e.g., attendance or study hours):
1. The values are compiled into a 1-row Pandas DataFrame.
2. Saved encoders (`encoders.pkl`) transform categorical strings to numerical labels.
3. The pre-trained Decision Tree classifier and regressor (`.pkl` models) generate live predictions.
4. The UI renders the predicted tier badge, score progress bar, and prescriptive recommendations.

#### Q17: How did you save and reload the trained machine learning models?
**Answer:**  
We used Python's `pickle` library for object serialization:
- **Saving**: `pickle.dump(model, open("models/decision_tree_classifier.pkl", "wb"))`
- **Loading**: `model = pickle.load(open("models/decision_tree_classifier.pkl", "rb"))`

#### Q18: What is the Batch Prediction feature in your app?
**Answer:**  
It allows a teacher or administrator to upload a CSV file containing hundreds of student records. The system processes the entire batch, runs inferences for each student simultaneously, displays the annotated table with predicted grades, and provides a one-click button to download the results CSV.

---

### Summary Tips for the Examiner:
- Speak clearly and with confidence.
- Emphasize the **practical academic value** of the project: helping at-risk students pass.
- Demonstrate the live Streamlit dashboard and show the Decision Tree diagram.
