# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 3 - Python Programming Fundamentals
# TOPIC:  Exception Handling (try, except, else, finally & Custom Errors)
# ==============================================================================

# --- 1. Handling Specific Exceptions (ZeroDivisionError & TypeError) ---
def safe_divide(numerator, denominator):
    """Safely calculates division while catching common mathematical errors."""
    try:
        result = numerator / denominator
    except ZeroDivisionError:
        print("[ERROR] Division by zero encountered! Returning 0.0 by default.")
        return 0.0
    except TypeError:
        print("[ERROR] Invalid data type provided! Both inputs must be numbers.")
        return None
    else:
        # Executes ONLY if no exceptions were raised
        print(f"[SUCCESS] Division calculation successful: {result}")
        return result
    finally:
        # Executes ALWAYS regardless of success or failure (used for cleanup)
        print("--- Execution block complete ---\n")

print("--- 1. SPECIFIC EXCEPTION HANDLING ---")
safe_divide(100, 4)
safe_divide(50, 0)
safe_divide(10, "invalid_str")


# --- 2. Catching Generic Exceptions & File Operations ---
print("--- 2. FILE INGESTION EXCEPTION HANDLING ---")
try:
    # Attempting to open a non-existent file
    with open("non_existent_dataset.csv", "r") as file:
        data = file.read()
except FileNotFoundError as e:
    print(f"[CATCH] Target file not found on disk: {e}")
except Exception as e:
    # Catch-all for unexpected pipeline errors
    print(f"[CRITICAL] Unexpected error occurred: {e}")


# --- 3. Raising Custom Exceptions ---
print("\n--- 3. CUSTOM DATA VALIDATION CHECKS ---")
def validate_age_for_model(age):
    """Validates patient age inputs before feeding into ML model."""
    if age < 0:
        raise ValueError("Age cannot be negative for clinical predictions.")
    return f"Valid Age Input: {age}"

try:
    print(validate_age_for_model(-5))
except ValueError as err:
    print(f"[VALIDATION FAILED] {err}")