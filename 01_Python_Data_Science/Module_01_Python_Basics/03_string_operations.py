# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 1 - Python Basics
# TOPIC:  String Operations (Comprehensive Reference)
# ==============================================================================

# --- 1. Indexing & Slicing (Positive & Negative) ---
raw_data = "IBM_Data_Science_2026"

print("--- STRING INDEXING & SLICING ---")
# Positive Indexing (Starts at 0)
print(f"First character (index 0): {raw_data[0]}") 

# Negative Indexing (Starts from the back at -1)
print(f"Last character (index -1): {raw_data[-1]}")

# Slicing: [start:stop:step]
print(f"Slice company name [0:3]: {raw_data[0:3]}")
print(f"Slice year [-4:]: {raw_data[-4:]}")
print(f"Stride slicing (every 2nd char): {raw_data[::2]}\n")


# --- 2. Escape Sequences & Multi-line Strings ---
print("--- ESCAPE SEQUENCES ---")
# \n (New line) and \t (Tab space)
print("Data Science Path:\n\t-> Basics\n\t-> Advanced")
# Escaping special quotes or backslashes
print("Learning Python's \"Strings\" is essential.\\\n")


# --- 3. Essential String Methods (Data Cleaning Focus) ---
print("--- STRING METHODS (DATA SANITIZATION) ---")
dirty_input = "   ai & Machine LEARNING portfolio   "

# Stripping whitespace & changing casing
clean_upper = dirty_input.strip().upper()
print(f"Original: '{dirty_input}'")
print(f"Sanitized & Upper: '{clean_upper}'")

# Find & Replace operations
replaced_text = clean_upper.replace("&", "AND")
print(f"Replace operation: {replaced_text}")

# Find index of a substring
substring_index = raw_data.find("Data")
print(f"Index position of 'Data' in '{raw_data}': {substring_index}")

# Split operation (Converts a string into a List of substrings)
data_list = raw_data.split("_")
print(f"Splitting text on underscore '_': {data_list}")