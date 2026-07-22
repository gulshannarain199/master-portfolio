# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 2 - Python Data Structures
# TOPIC:  Lists (Mutable & Dynamic Data Handling)
# ==============================================================================

# --- 1. List Creation & Mutability ---
# A dynamic list of sensor readings (Temperature in Celsius)
temperature_logs = [22.4, 21.8, 23.1, 22.9]

print("--- INITIAL LIST & MUTABILITY ---")
print(f"Original Logs: {temperature_logs}")

# Modifying an element directly (Proving Mutability)
temperature_logs[0] = 22.5
print(f"Updated Logs (Index 0 changed): {temperature_logs}\n")


# --- 2. Essential List Operations (Append, Extend, Insert) ---
print("--- LIST MANIPULATION ---")
# .append() adds a SINGLE element to the end
temperature_logs.append(24.0)
print(f"After append(24.0): {temperature_logs}")

# .extend() concatenates another list/collection to the end
new_batch = [23.5, 22.1]
temperature_logs.extend(new_batch)
print(f"After extend([23.5, 22.1]): {temperature_logs}")

# .insert() adds an element at a specific index
temperature_logs.insert(1, 21.9)
print(f"After insert(index 1, 21.9): {temperature_logs}\n")


# --- 3. Removing Elements (del, .pop(), .remove()) ---
print("--- DELETION METHODS ---")
# del statement removes by index position
del temperature_logs[0]
print(f"After del index 0: {temperature_logs}")

# .pop() removes and RETURNS the last element (or specified index)
popped_value = temperature_logs.pop()
print(f"Popped Value: {popped_value} | Remaining List: {temperature_logs}")

# .remove() finds and removes the FIRST occurrence of a specific value
temperature_logs.remove(23.1)
print(f"After remove(23.1): {temperature_logs}\n")


# --- 4. Advanced Slicing & Aliasing vs. Cloning ---
print("--- ALIASING VS. COPYING (CRITICAL DATA SCIENCE CONCEPT) ---")
original_list = ["A", "B", "C"]

# Aliasing (Both variables point to the EXACT SAME memory location)
alias_list = original_list
alias_list[0] = "Z"
print(f"Original after modifying alias: {original_list} (Alias modified both!)")

# Cloning / Shallow Copy (Creates an independent copy)
copied_list = original_list.copy()  # or original_list[:]
copied_list[0] = "A"
print(f"Original: {original_list} | Independent Copy: {copied_list}")