# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 4 - Working with Data in Python
# TOPIC:  Pandas Basics (Series, DataFrames, Slicing & Indexing)
# ==============================================================================

import pandas as pd

# --- 1. Creating DataFrames from Dictionaries ---
print("--- 1. DATAFRAME CREATION ---")
data_dict = {
    "Employee_ID": [101, 102, 103, 104, 105],
    "Department": ["Data Engineering", "Data Science", "DevOps", "Data Engineering", "Data Analytics"],
    "Salary_USD": [95000, 110000, 88000, 102000, 78000],
    "Years_Experience": [3, 5, 2, 4, 1]
}

df = pd.DataFrame(data_dict)
print("Employee DataFrame:")
print(df)


# --- 2. Dataset Inspection Methods ---
print("\n--- 2. DATAFRAME INSPECTION ---")
print("First 2 rows (head):")
print(df.head(2))

print("\nDataFrame Summary Info:")
df.info()

print("\nStatistical Overview (describe):")
print(df.describe())


# --- 3. Selecting Columns & Filtering Rows ---
print("\n--- 3. SELECTION & FILTERING ---")
# Extracting a single column (returns a Series)
dept_series = df["Department"]
print("Department Column (Series):")
print(dept_series.head(2))

# Filtering rows based on condition (Boolean Indexing)
high_earners = df[df["Salary_USD"] > 90000]
print("\nHigh Earners (> $90k):")
print(high_earners)


# --- 4. Indexing with loc[] and iloc[] ---
print("\n--- 4. LOC VS ILOC INDEXING ---")
# loc uses labels/conditions, iloc uses integer index positions
print("First record using .iloc[0]:")
print(df.iloc[0])

print("\nSpecific cell selection using .iloc[1, 2] (Row 1, Col 2 - Salary):")
print(f"Salary: ${df.iloc[1, 2]}")