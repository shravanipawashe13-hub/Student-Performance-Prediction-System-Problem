# Step-by-Step Power BI Dashboard Development Guide
## Student Performance Prediction & Academic Analytics System

This guide is designed for **BCA college project reviews, practical exams, and presentations**. Follow these step-by-step instructions to create an interactive 3-page business intelligence dashboard in **Microsoft Power BI Desktop**.

---

## 1. Preparing the Environment & Data Ingestion

### Step 1.1: Open Power BI Desktop
1. Launch **Power BI Desktop** (free from Microsoft Store or powerbi.microsoft.com).
2. On the startup splash screen, click **Get Data** or click **Get Data -> Text/CSV** from the Home ribbon.

### Step 1.2: Import Dataset
1. Browse to your project folder:
   `Student Performance Prediction System/data/student_performance_powerbi.csv`
2. In the preview window, confirm that delimiter is set to **Comma (,)** and data encoding is **UTF-8**.
3. Click **Transform Data** (Power Query Editor).

### Step 1.3: Verify Data Types in Power Query
Ensure the columns have the following detected data types:
| Column Name | Data Type | Notes |
| :--- | :--- | :--- |
| `Student_ID` | Text | Unique Key (STU1001...) |
| `Age`, `Study_Hours_Per_Week`, `Attendance_Rate` | Decimal Number / Whole Number | Numerical features |
| `Past_Exam_Score`, `Internal_Assessment_Score` | Decimal Number | Academic indicators |
| `Assignment_Completion_Rate`, `Sleep_Hours_Per_Day` | Decimal Number | Behavioral factors |
| `Final_Score`, `Grade_Point` | Decimal Number | Target metrics |
| `Gender`, `Parental_Education`, `Performance_Category` | Text | Categorical dimensions |
| `Tutoring_Classes`, `Internet_Access`, `Passed` | Text | Binary indicators (Yes/No) |
| `Attendance_Group`, `Study_Hours_Group`, `Risk_Level` | Text | Enriched grouping fields |

Click **Close & Apply** in the top-left corner of the Power Query Editor.

### Step 1.4: Apply the Custom Project Theme
1. In Power BI Desktop, navigate to the **View** ribbon.
2. Click the dropdown arrow on the **Themes gallery**.
3. Select **Browse for themes**.
4. Choose the file:
   `Student Performance Prediction System/powerbi/powerbi_theme.json`
5. Power BI will instantly apply modern slate/dark styling, custom visual padding, and curated color palettes.

---

## 2. Setting Up DAX Measures

Go to the **Modeling** ribbon -> Click **New Measure** and add each measure from `powerbi/dax_measures.txt`:

1. `Total Students = COUNTROWS('student_performance_powerbi')`
2. `Passed Students = CALCULATE(COUNTROWS('student_performance_powerbi'), 'student_performance_powerbi'[Passed] = "Yes")`
3. `Pass Rate % = DIVIDE([Passed Students], [Total Students], 0) * 100`
4. `Average Final Score = ROUND(AVERAGE('student_performance_powerbi'[Final_Score]), 1)`
5. `Average Attendance % = ROUND(AVERAGE('student_performance_powerbi'[Attendance_Rate]), 1)`
6. `Average Study Hours = ROUND(AVERAGE('student_performance_powerbi'[Study_Hours_Per_Week]), 1)`
7. `High Risk Students = CALCULATE(COUNTROWS('student_performance_powerbi'), 'student_performance_powerbi'[Risk_Level] = "High Risk")`
8. `High Risk % = DIVIDE([High Risk Students], [Total Students], 0) * 100`

---

## 3. Designing Dashboard Pages

Create 3 dedicated report pages at the bottom tabs:

### Page 1: 📊 Executive Academic Overview
*Purpose: High-level summary of university/college student performance.*

- **Top KPI Cards Row**:
  - **Card 1**: `Total Students` (1,200)
  - **Card 2**: `Pass Rate %` (with gauge or percentage format)
  - **Card 3**: `Average Final Score` (Marks out of 100)
  - **Card 4**: `Average Attendance %`
  - **Card 5**: `High Risk Students` (Highlighted in red/coral)
- **Top-Right Slicers**:
  - Slicer 1: `Gender` (Tile/Button layout)
  - Slicer 2: `Parental_Education` (Dropdown)
- **Visual 1 (Donut Chart)**:
  - **Legend**: `Performance_Category` (Distinction, Merit, Pass, At-Risk)
  - **Values**: `Total Students`
- **Visual 2 (Clustered Column Chart)**:
  - **X-axis**: `Attendance_Group`
  - **Y-axis**: `Average Final Score`
  - **Legend**: `Passed`
- **Visual 3 (Stacked Bar Chart)**:
  - **Y-axis**: `Parental_Education`
  - **X-axis**: `Total Students`
  - **Legend**: `Performance_Category`

---

### Page 2: 🔬 Behavioral & Lifestyle Analytics
*Purpose: Demonstrating correlation between study habits, sleep, tutoring, and academic outcomes.*

- **Visual 1 (Scatter Plot)**:
  - **X-axis**: `Study_Hours_Per_Week`
  - **Y-axis**: `Final_Score`
  - **Details**: `Student_ID`
  - **Legend**: `Passed`
- **Visual 2 (Clustered Bar Chart)**:
  - **Y-axis**: `Tutoring_Classes` (Yes vs No)
  - **X-axis**: `Average Final Score`
- **Visual 3 (Line Chart - Optimal Sleep Curve)**:
  - **X-axis**: `Sleep_Hours_Per_Day`
  - **Y-axis**: `Average Final Score`
  - *Observation for viva*: Shows clear bell-shaped curve peaking between 7 to 8 hours of sleep.
- **Visual 4 (100% Stacked Column Chart)**:
  - **X-axis**: `Study_Hours_Group`
  - **Y-axis**: `Total Students`
  - **Legend**: `Performance_Category`

---

### Page 3: 🚨 Early Warning & Student Intervention Matrix
*Purpose: Operational dashboard for college faculty to identify students requiring immediate tutoring or attendance counseling.*

- **Top Alert Slicer**:
  - Slicer: `Risk_Level` (High Risk, Moderate Risk, Low Risk)
- **Visual 1 (Matrix / Table)**:
  - **Columns**: `Student_ID`, `Attendance_Rate`, `Internal_Assessment_Score`, `Study_Hours_Per_Week`, `Final_Score`, `Risk_Level`, `Student Intervention Status`
  - **Conditional Formatting**:
    - Apply **Data Bars** or **Red Background** to `Attendance_Rate` when `< 65%`.
    - Apply **Status Icons** to `Risk_Level`.
- **Visual 2 (Gauge Chart)**:
  - **Value**: `Average Attendance %`
  - **Target**: `75%` (Mandatory University Rule)
  - **Minimum**: `0`, **Maximum**: `100`

---

## 4. Key Talking Points for Project Viva / Presentation

When explaining this Power BI component to the external examiner:

1. **Why Power BI alongside Python?**
   > *"While Python and Scikit-Learn handle machine learning modeling and predictive inference, Power BI bridges the gap for institutional decision-makers (principals, HODs, mentors) by offering real-time interactive slicing, drill-throughs, and early warning notifications without writing code."*

2. **Data Pipeline Flow**:
   > *Raw Student Data $\rightarrow$ Python Preprocessing (Pandas) $\rightarrow$ Cleaned & Enriched Schema $\rightarrow$ Scikit-Learn Decision Trees (Predictions) $\rightarrow$ Power BI Dashboard (Executive Reporting).*

3. **DAX Measures**:
   > Explain how you utilized `CALCULATE`, `DIVIDE`, and `SWITCH` functions to dynamically evaluate at-risk criteria and generate actionable intervention recommendations.
