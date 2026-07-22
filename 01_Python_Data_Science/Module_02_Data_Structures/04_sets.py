# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 2 - Python Data Structures
# TOPIC:  Sets (Unordered, Unique Collections & Mathematical Logic)
# ==============================================================================

# --- 1. Deduplication (Converting Lists to Sets) ---
# Raw user IDs containing duplicates from database logging
raw_user_logs = [101, 102, 105, 101, 103, 102, 108, 105]

# Passing a list to set() automatically filters out duplicates
unique_users = set(raw_user_logs)

print("--- DATA DEDUPLICATION ---")
print(f"Raw Log Count: {len(raw_user_logs)} | Data: {raw_user_logs}")
print(f"Unique Users Count: {len(unique_users)} | Data: {unique_users}\n")


# --- 2. Set Operations (Add, Remove, Check Membership) ---
print("--- SET MANIPULATION ---")
# .add() appends a unique item
unique_users.add(109)
print(f"After add(109): {unique_users}")

# .remove() deletes an item
unique_users.remove(101)
print(f"After remove(101): {unique_users}")

# Fast membership testing using 'in' keyword
print(f"Is user 102 active? {102 in unique_users}")
print(f"Is user 101 active? {101 in unique_users}\n")


# --- 3. Venn Diagram Logic (Intersections, Unions, Differences) ---
# Two sets of customer cohorts from different marketing campaigns
campaign_A_leads = {"alice@test.com", "bob@test.com", "charlie@test.com"}
campaign_B_leads = {"bob@test.com", "david@test.com", "charlie@test.com", "eve@test.com"}

print("--- MATHEMATICAL SET OPERATIONS ---")
print(f"Campaign A: {campaign_A_leads}")
print(f"Campaign B: {campaign_B_leads}\n")

# Intersection (&): Elements present in BOTH sets
overlapping_leads = campaign_A_leads.intersection(campaign_B_leads)
print(f"Overlapping Leads (Intersection &): {overlapping_leads}")

# Union (|): All combined unique elements across BOTH sets
all_distinct_leads = campaign_A_leads.union(campaign_B_leads)
print(f"All Distinct Leads (Union |): {all_distinct_leads}")

# Difference (-): Elements in Campaign A that are NOT in Campaign B
exclusive_A_leads = campaign_A_leads.difference(campaign_B_leads)
print(f"Leads ONLY in Campaign A (Difference -): {exclusive_A_leads}")

# Subset check (issubset)
print(f"Is Campaign A a subset of all distinct leads? {campaign_A_leads.issubset(all_distinct_leads)}")