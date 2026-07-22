# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# TOPIC:  Automated Repository Error & Syntax Audit
# ==============================================================================

import os
import subprocess

# List of all primary reference scripts across your modules
scripts_to_audit = [
    "Module_01_Python_Basics/01_data_types.py",
    "Module_01_Python_Basics/02_expressions_variables.py",
    "Module_01_Python_Basics/03_string_operations.py",
    "Module_02_Data_Structures/01_tuples.py",
    "Module_02_Data_Structures/02_lists.py",
    "Module_02_Data_Structures/03_dictionaries.py",
    "Module_02_Data_Structures/04_sets.py",
    "Module_03_Python_Fundamentals/01_conditions_branching.py",
    "Module_03_Python_Fundamentals/02_loops.py",
    "Module_03_Python_Fundamentals/03_functions.py",
    "Module_03_Python_Fundamentals/04_exception_handling.py",
    "Module_03_Python_Fundamentals/05_objects_classes.py",
    "Module_04_Working_With_Data/01_reading_writing_files.py",
    "Module_04_Working_With_Data/02_pandas_basics.py",
    "Module_04_Working_With_Data/03_numpy_basics.py",
    "Module_05_APIs_Data_Collection/01_simple_apis.py",
    "Module_05_APIs_Data_Collection/02_web_scraping.py",
    "Module_05_APIs_Data_Collection/03_working_with_files.py"
]

print("=== STARTING COMPREHENSIVE REPOSITORY AUDIT ===")
passed_count = 0
failed_count = 0

for script in scripts_to_audit:
    if not os.path.exists(script):
        print(f"[MISSING] {script} file not found.")
        failed_count += 1
        continue
    
    # Run each script as a subprocess to check for runtime or syntax errors
    result = subprocess.run(["python", script], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[PASS] {script}")
        passed_count += 1
    else:
        print(f"[FAIL] {script}")
        print(f"       Error details: {result.stderr.strip()}")
        failed_count += 1

print("\n=== AUDIT SUMMARY ===")
print(f"Total Scripts Checked: {len(scripts_to_audit)}")
print(f"Passed Successfully:   {passed_count}")
print(f"Failed / Errors:       {failed_count}")