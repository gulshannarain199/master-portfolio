# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 4 - Working with Data in Python
# TOPIC:  Reading & Writing Files (File I/O, Context Managers)
# ==============================================================================

import os

# Define temporary file paths for file I/O operations
data_file_path = "sample_data_log.txt"

# --- 1. Writing Files using Context Manager ('w' and 'a' modes) ---
print("--- 1. WRITING DATA TO FILE ---")

# Using 'with' (context manager) ensures automatic file closing
with open(data_file_path, "w") as file:
    file.write("Timestamp,Metric,Value\n")
    file.write("2026-07-21 10:00:00,CPU_Usage,45.2\n")
    file.write("2026-07-21 10:05:00,CPU_Usage,52.8\n")

print(f"Dataset successfully created and written to '{data_file_path}'.")

# Appending new records using 'a' mode
with open(data_file_path, "a") as file:
    file.write("2026-07-21 10:10:00,CPU_Usage,61.0\n")

print("Appended new log entry to dataset file.\n")


# --- 2. Reading Files ('r' mode, read(), readline(), readlines()) ---
print("--- 2. READING DATA FROM FILE ---")

# Reading entire file into a single string using .read()
with open(data_file_path, "r") as file:
    entire_content = file.read()
    print("[.read() Output]:")
    print(entire_content)

# Reading file line by line into a list using .readlines()
with open(data_file_path, "r") as file:
    lines_list = file.readlines()
    print(f"[.readlines() Output]: List length = {len(lines_list)} lines")
    for idx, line in enumerate(lines_list):
        print(f"Line {idx}: {line.strip()}")


# --- 3. Cleanup Operations ---
if os.path.exists(data_file_path):
    os.remove(data_file_path)
    print(f"\n[CLEANUP] Temporary file '{data_file_path}' removed.")