# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 2 - Python Data Structures
# TOPIC:  Dictionaries (Key-Value Data Mapping)
# ==============================================================================

# --- 1. Creating Dictionaries & Key-Value Lookups ---
# Storing structured record metadata for a Data Science student
student_profile = {
    "student_id": 8842,
    "name": "Gulshan",
    "course": "IBM Data Science",
    "modules_completed": 1,
    "is_active": True
}

print("--- DICTIONARY ACCESS & LOOKUPS ---")
print(f"Full Profile: {student_profile}")
# Direct Key Lookup
print(f"Student Name: {student_profile['name']}")
# Safe Access using .get() (Prevents KeyErrors if key is missing)
print(f"Modules Completed (via .get()): {student_profile.get('modules_completed')}")
print(f"Non-existent key default check: {student_profile.get('gpa', 'Not Assigned')}\n")


# --- 2. Modifying, Adding & Deleting Entries ---
print("--- MUTABILITY & UPDATES ---")
# Adding a new key-value pair
student_profile["gpa"] = 3.95
print(f"After adding GPA: {student_profile}")

# Updating an existing value
student_profile["modules_completed"] = 2
print(f"After completing Module 2: {student_profile}")

# Deleting an entry using del
del student_profile["is_active"]
print(f"After removing 'is_active' status: {student_profile}\n")


# --- 3. Dictionary Inspection Methods ---
print("--- INSPECTION & ITERATION METHODS ---")
# Extracting all keys, values, and items
print(f"Keys: {list(student_profile.keys())}")
print(f"Values: {list(student_profile.values())}")
print(f"Items (Tuples of Key-Value pairs): {list(student_profile.items())}\n")


# --- 4. Nested Dictionaries (Complex Data Structures) ---
print("--- NESTED DICTIONARY STRUCTURING ---")
database = {
    "user_101": {
        "name": "Alice",
        "scores": [95, 88, 92]
    },
    "user_102": {
        "name": "Bob",
        "scores": [78, 85, 80]
    }
}

# Accessing nested elements
alice_second_score = database["user_101"]["scores"][1]
print(f"Alice's 2nd Exam Score: {alice_second_score}")