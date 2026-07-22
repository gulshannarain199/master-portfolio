# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 5 - APIs and Data Collection
# TOPIC:  Working with Different File Formats (CSV & JSON Persistence)
# ==============================================================================

import requests
import pandas as pd
import json

print("--- 1. FETCHING DATA FOR EXPORT ---")
url = "https://jsonplaceholder.typicode.com/todos"
response = requests.get(url)

if response.status_code == 200:
    todos = response.json()[:10]  # Grab the first 10 records for demonstration
    
    # --- 2. Saving Data as JSON ---
    json_filename = "Module_05_APIs_Data_Collection/todos_export.json"
    with open(json_filename, "w") as json_file:
        json.dump(todos, json_file, indent=4)
    print(f"Successfully saved data to: {json_filename}")

    # --- 3. Converting to Pandas and Saving as CSV ---
    df = pd.DataFrame(todos)
    csv_filename = "Module_05_APIs_Data_Collection/todos_export.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Successfully saved DataFrame to CSV: {csv_filename}")
    
    # --- 4. Quick Verification Reading ---
    print("\n--- 4. VERIFYING SAVED CSV ---")
    saved_df = pd.read_csv(csv_filename)
    print(saved_df[["id", "title", "completed"]].head(3))