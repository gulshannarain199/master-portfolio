# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 5 - APIs and Data Collection
# TOPIC:  Simple APIs, HTTP Requests, Status Codes & JSON Processing
# ==============================================================================

import requests
import pandas as pd

# --- 1. Making a Basic HTTP GET Request ---
print("--- 1. HTTP GET REQUEST & RESPONSE STATUS ---")
# Public public API endpoint returning dummy user data
url = "https://jsonplaceholder.typicode.com/users"

response = requests.get(url)

print(f"Target URL: {url}")
print(f"Status Code: {response.status_code}")  # 200 means OK / Success
print(f"Response Header (Content-Type): {response.headers.get('Content-Type')}")


# --- 2. Extracting and Parsing JSON Data ---
print("\n--- 2. PARSING JSON DATA ---")
if response.status_code == 200:
    data = response.json()  # Converts JSON response into native Python list/dict
    
    print(f"Total Records Received: {len(data)}")
    print(f"First Record Preview (Name): {data[0]['name']}")
    print(f"First Record Preview (Email): {data[0]['email']}")


# --- 3. Converting API Data to Pandas DataFrame ---
print("\n--- 3. DATAFRAME INTEGRATION ---")
# Convert the list of JSON dictionaries directly into a DataFrame
df = pd.DataFrame(data)

# Select key columns for display
clean_df = df[["id", "name", "username", "email", "phone"]]
print("API Data Transformed into DataFrame:")
print(clean_df.head(3))