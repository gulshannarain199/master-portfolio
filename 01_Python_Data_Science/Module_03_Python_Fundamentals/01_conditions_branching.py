# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 3 - Python Programming Fundamentals
# TOPIC:  Conditions & Branching (Control Flow)
# ==============================================================================

# --- 1. Basic Comparison Operators & Branching ---
memory_usage_pct = 84.5

print("--- SYSTEM RESOURCE ALERT CHECK ---")
if memory_usage_pct >= 90.0:
    print("CRITICAL: Memory usage exceeds 90%! Triggering automatic process dump.")
elif memory_usage_pct >= 75.0:
    print(f"WARNING: High memory usage detected ({memory_usage_pct}%). Monitoring closely.")
else:
    print("OK: Memory usage within normal operational parameters.")


# --- 2. Logical Operators (and, or, not) ---
null_count = 0
data_type_valid = True
record_count = 1500

print("\n--- DATA PIPELINE HEALTH CHECK ---")
if (null_count == 0 and data_type_valid) and (record_count > 1000):
    print("PIPELINE STATUS: PASS - Data ingest batch validated successfully.")
else:
    print("PIPELINE STATUS: FAIL - Data batch contains quality anomalies.")

system_locked = False
if not system_locked:
    print("ACCESS CONTROL: System unlocked, proceeding with batch ingestion.")


# --- 3. Nested Branching Logic ---
transaction_amount = 12500.00
is_foreign_ip = True
account_age_days = 15

print("\n--- TRANSACTION FRAUD RISK ENGINE ---")
if transaction_amount > 10000.00:
    if is_foreign_ip or account_age_days < 30:
        print("FLAGGED: High-value transaction from new/foreign source. Hold for review.")
    else:
        print("APPROVED: High-value transaction from verified trusted entity.")
else:
    print("APPROVED: Standard transaction auto-cleared.")