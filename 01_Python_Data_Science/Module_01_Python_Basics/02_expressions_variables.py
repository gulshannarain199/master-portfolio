# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 1 - Python Basics
# TOPIC:  Expressions and Variables
# ==============================================================================

# --- 1. Basic Mathematical Expressions ---
monthly_income = 5000
rent = 1200
groceries = 450.75
utilities = 200

# Total Expenses (Addition and Subtraction)
total_expenses = rent + groceries + utilities
savings = monthly_income - total_expenses

print("--- MONTHLY FINANCIAL SUMMARY ---")
print(f"Total Income: ${monthly_income}")
print(f"Total Expenses: ${total_expenses}")
print(f"Net Savings: ${savings}\n")


# --- 2. Division Types (Standard vs. Integer Division & Modulo) ---
print("--- DIVISION & MODULO BEHAVIOR ---")
# Standard Division (/) always returns a Float
weekly_grocery_budget_float = groceries / 4
print(f"Standard Division (groceries / 4): {weekly_grocery_budget_float} (Type: {type(weekly_grocery_budget_float)})")

# Integer/Floor Division (//) rounds down to the nearest whole integer
weekly_grocery_budget_int = groceries // 4
print(f"Floor Division (groceries // 4): {weekly_grocery_budget_int} (Type: {type(weekly_grocery_budget_int)})")

# Modulo (%) finds the remainder
leftover_groceries = groceries % 4
print(f"Modulo Remainder (groceries % 4): ${leftover_groceries:.2f}\n")


# --- 3. Operator Precedence (PEMDAS / Order of Operations) ---
print("--- OPERATOR PRECEDECE (PEMDAS) ---")
calculation_1 = 100 + 50 * 2    # 50 * 2 first
calculation_2 = (100 + 50) * 2  # Parentheses first

print(f"100 + 50 * 2 = {calculation_1}")
print(f"(100 + 50) * 2 = {calculation_2}\n")


# --- 4. Variable Re-assignment & Dynamic State Updates ---
print("--- VARIABLE RE-ASSIGNMENT ---")
portfolio_value = 1000
print(f"Initial Investment: ${portfolio_value}")

portfolio_value += 250  # Add deposit
print(f"After Deposit (+250): ${portfolio_value}")

portfolio_value *= 1.10  # 10% market compound growth
print(f"After 10% Market Growth (*= 1.10): ${portfolio_value:.2f}")