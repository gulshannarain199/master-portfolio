# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 1 - Python Basics
# TOPIC:  Types & Type Casting (Comprehensive)
# ==============================================================================
import sys

# --- 1. Primitive Data Types ---
user_name = "Alex Rivera"  # String (str)
daily_steps = 8450         # Integer (int)
distance_km = 6.28         # Float (float)
goal_achieved = True       # Boolean (bool)

print("--- FITNESS DASHBOARD ---")
print(f"User: {user_name} ({type(user_name)})")
print(f"Steps Taken: {daily_steps} ({type(daily_steps)})")
print(f"Distance: {distance_km} km ({type(distance_km)})")
print(f"Daily Goal Achieved? {goal_achieved} ({type(goal_achieved)})")
print("-------------------------\n")


# --- 2. Type Casting Demonstrations ---
print("--- TYPE CASTING OPERATIONS ---")

# Converting Float to Integer (Truncates/downcasts the decimals)
rounded_distance = int(distance_km)
print(f"Float to Int: {distance_km} -> {rounded_distance} ({type(rounded_distance)})")

# Converting String to Integer
string_steps = "10000"
converted_steps = int(string_steps)
print(f"String to Int: '{string_steps}' -> {converted_steps} ({type(converted_steps)})")

# Converting Integer to Float
float_steps = float(daily_steps)
print(f"Int to Float: {daily_steps} -> {float_steps} ({type(float_steps)})")


# --- 3. Edge Cases & Casting Failures ---
print("\n--- CASTING LIMITATIONS & TRUTHY/FALSY ---")

# ERROR HANDLING NOTE: Un-commenting the line below will throw a ValueError:
# invalid_cast = int("Alex Rivera") 

print("[NOTE]: Cannot cast non-numeric strings to int/float (results in ValueError).")

# String to Boolean casting rules
print(f"Populated string to Boolean: bool('Alex') -> {bool('Alex')}") # True
print(f"Empty string to Boolean: bool('') -> {bool('')}")             # False


# --- 4. Boolean Behind the Scenes ---
print("\n--- BOOLEAN CASTING & MATH ---")
print(f"Integer 1 cast to Boolean: {bool(1)}")
print(f"Integer 0 cast to Boolean: {bool(0)}")
print(f"True evaluated as Integer: {int(True)}")
print(f"False evaluated as Integer: {int(False)}")
print(f"Math calculation (True + True): {True + True}")


# --- 5. Data Science Memory Insight (Advanced Type Awareness) ---
print("\n--- MEMORY FOOTPRINT BY TYPE (Bytes) ---")
print(f"Integer ({daily_steps}): {sys.getsizeof(daily_steps)} bytes")
print(f"Float ({distance_km}): {sys.getsizeof(distance_km)} bytes")
print(f"String ('{user_name}'): {sys.getsizeof(user_name)} bytes")