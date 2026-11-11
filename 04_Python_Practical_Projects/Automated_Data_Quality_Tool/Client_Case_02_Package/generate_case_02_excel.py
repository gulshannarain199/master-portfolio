"""Generate the synthetic Excel input for Client Case Study 02."""
from pathlib import Path
from openpyxl import Workbook

PACKAGE = Path(__file__).resolve().parent
OUTPUT = PACKAGE / "Regional_East.xlsx"

workbook = Workbook()
sheet = workbook.active
sheet.title = "East Customers"
sheet.append([
    "Account Number", "Resident Name", "Contact Email",
    "District", "Mobile", "Division",
])
sheet.append(["E-3001", "Amelia Clarke", "amelia@example.com", "Rose Hill", "52520001", "Finance"])
sheet.append(["E-3002", "Brian Lee", "brian@example.com", "Curepipe", "52520002", "Operations"])
sheet.append(["E-3003", "Chloe Martin", "shared@example.com", "Quatre Bornes", "52520003", "Sales"])
sheet.append(["E-3004", "Daniel Wong", "daniel@example.com", "Port Louis", "52520004", "IT"])
workbook.save(OUTPUT)
workbook.close()
print(f"Created synthetic input: {OUTPUT}")
