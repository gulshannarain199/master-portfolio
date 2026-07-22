# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 2 - Python Data Structures
# TOPIC:  Tuples (Ordered & Immutable)
# ==============================================================================

# --- 1. Tuple Creation & Content Heterogeneity ---
# Creating a geospatial checkpoint tuple: (Station_ID, Latitude, Longitude, Active_Status)
checkpoint_alpha = (101, 34.0522, -118.2437, True)

print("--- TUPLE PROPERTIES ---")
print(f"Checkpoint Tuple: {checkpoint_alpha}")
print(f"Data Type: {type(checkpoint_alpha)}")
print(f"Length of Tuple: {len(checkpoint_alpha)}\n")


# --- 2. Indexing, Slicing & Negative Indexing ---
print("--- INDEXING & SLICING ---")
print(f"Station ID (Index 0): {checkpoint_alpha[0]}")
print(f"Status (Negative Index -1): {checkpoint_alpha[-1]}")

# Slicing a sub-tuple (Extracting Lat/Lon coordinates)
coordinates = checkpoint_alpha[1:3]
print(f"Extracted Coordinates Slice [1:3]: {coordinates} (Type: {type(coordinates)})\n")


# --- 3. Immutability Principle ---
print("--- IMMUTABILITY PROOF ---")
print("[NOTE] Tuples cannot be modified after creation.")
# Un-commenting the line below would trigger a TypeError:
# checkpoint_alpha[1] = 35.1234 


# --- 4. Nesting and Sorting ---
# A tuple containing nested tuple data
nested_data = (101, (34.0522, -118.2437), "Sensor_Active", (45, 12, 89))
print(f"Nested Latitude Access: {nested_data[1][0]}")

# Sorting a tuple: sorted() returns a NEW sorted list, keeping original tuple intact
unordered_scores = (55, 12, 98, 43, 22)
sorted_scores = sorted(unordered_scores)
print(f"\nOriginal Tuple: {unordered_scores}")
print(f"Sorted Output (List): {sorted_scores}")