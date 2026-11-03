"""
Example settings for a client file.

Copy the relevant settings into FILE_CONFIGS in run_pipeline.py.
Do not assume these example column names apply to every client.
"""

# Example 1: headerless file. The order MUST be confirmed with the client.
HEADERLESS_EXAMPLE = {
    "has_header": False,
    "column_order": ("CustomerID", "Name", "Email", "City", "Phone"),
}

# Example 2: file with headings that use non-standard names.
# Mapping keys are canonical fields; values are actual source headings.
CUSTOM_COLUMN_MAPPING_EXAMPLE = {
    "column_mapping": {
        "customerid": "Account Ref",
        "name": "Client Full Name",
        "email": "Email Contact",
        "city": "Town",
    }
}

# Example 3: XLSX file with a named worksheet.
WORKSHEET_EXAMPLE = {
    "sheet_name": "Customers",
}

# Duplicate matching defaults to ("name", "email", "city").
# Change only after the client confirms the rule:
DUPLICATE_RULE_EXAMPLE = {
    "duplicate_keys": ("name", "email"),
}
