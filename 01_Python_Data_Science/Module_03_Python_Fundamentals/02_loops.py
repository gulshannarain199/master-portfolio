# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 3 - Python Programming Fundamentals
# TOPIC:  Loops (for, while, range, enumerate, break/continue)
# ==============================================================================

# --- 1. For Loops & range() Function ---
print("--- 1. BATCH PROCESSING WITH FOR LOOPS ---")
# Simulating iteration over a dataset batch range
for batch_id in range(1, 4):
    print(f"Processing Data Batch #{batch_id}...")


# --- 2. Iterating Over Collections & enumerate() ---
print("\n--- 2. DATA EXTRACTION AND ENUMERATE ---")
sensor_readings = [21.5, 23.8, 19.4, 25.1, 22.0]

# Using enumerate() to track both index and value (Pythonic best practice)
for index, reading in enumerate(sensor_readings):
    print(f"Sensor ID [{index}]: Reading = {reading}°C")


# --- 3. Flow Control: break and continue ---
print("\n--- 3. DATA FILTERING WITH CONTINUE & BREAK ---")
data_stream = [100, 200, -999, 400, 500, "CORRUPT_EOF", 700]

for entry in data_stream:
    # Skip invalid missing indicator (-999) using continue
    if entry == -999:
        print("[SKIP] Missing value encountered (-999). Skipping record.")
        continue
    
    # Halt stream processing immediately if corrupt signal is detected
    if entry == "CORRUPT_EOF":
        print("[HALT] Critical corruption signal detected! Aborting loop.")
        break
        
    print(f"[INGESTED] Valid Data Entry: {entry}")


# --- 4. While Loops (Condition-Based Iteration) ---
print("\n--- 4. WHILE LOOP PROCESS RETRY MECHANISM ---")
connection_attempts = 0
max_retries = 3
database_connected = False

while not database_connected and connection_attempts < max_retries:
    connection_attempts += 1
    print(f"Attempting DB connection... (Attempt {connection_attempts}/{max_retries})")
    
    # Simulate successful connection on attempt 3
    if connection_attempts == 3:
        database_connected = True
        print("SUCCESS: Database connection established!")