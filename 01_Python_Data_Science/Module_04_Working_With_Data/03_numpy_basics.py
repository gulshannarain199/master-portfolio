# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 4 - Working with Data in Python
# TOPIC:  NumPy Fundamentals (1D/2D Arrays, Vectorization & Mathematical Broadcasting)
# ==============================================================================

import numpy as np

# --- 1. Creating 1D Arrays & Array Properties ---
print("--- 1. 1D ARRAY CREATION & ATTRIBUTES ---")
data_list = [10, 20, 30, 40, 50]
arr_1d = np.array(data_list)

print(f"1D Array: {arr_1d}")
print(f"Data Type (.dtype): {arr_1d.dtype}")
print(f"Dimensions (.ndim): {arr_1d.ndim}")
print(f"Shape (.shape): {arr_1d.shape}")


# --- 2. Vectorized Operations vs Python Loops ---
print("\n--- 2. VECTORIZED ARITHMETIC & BROADCASTING ---")
# Element-wise operations happen instantly across the entire array
arr_added = arr_1d + 5
arr_multiplied = arr_1d * 2

print(f"Original Array:     {arr_1d}")
print(f"Array + 5:          {arr_added}")
print(f"Array * 2:          {arr_multiplied}")


# --- 3. 2D Arrays (Matrices) & Universal Functions ---
print("\n--- 3. 2D ARRAYS & MATRIX OPERATIONS ---")
matrix_2d = np.array([[1, 2, 3], [4, 5, 6]])

print("2D Matrix:")
print(matrix_2d)
print(f"2D Shape: {matrix_2d.shape}")

# Matrix transposition & universal math functions
print(f"\nTransposed Matrix (.T):\n{matrix_2d.T}")
print(f"Sum of all elements: {np.sum(matrix_2d)}")
print(f"Mean of elements:    {np.mean(matrix_2d)}")


# --- 4. Indexing & Slicing in 2D ---
print("\n--- 4. 2D ARRAY SLICING ---")
# Row 0, Column 1 (0-indexed)
print(f"Specific Element [0, 1]: {matrix_2d[0, 1]}")
# Extracting all rows, column index 2
print(f"Extracting Column 2:     {matrix_2d[:, 2]}")