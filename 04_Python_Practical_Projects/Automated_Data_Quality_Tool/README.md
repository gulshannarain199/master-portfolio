# Automated Data Quality Tool

A Python tool for inspecting and cleaning customer-style CSV and Excel (`.xlsx`) files. It is intended for careful, reviewable data-cleaning work—not for silently changing client records.

## What it does

- Reads CSV and XLSX input files from `input/` without modifying them.
- Preserves original source columns, CustomerIDs, and source-row references.
- Standardizes names and email addresses in the cleaned output. Other configured text fields are trimmed; CustomerIDs are preserved.
- Removes only exact duplicates under the configured duplicate-key rule (default: Name + Email + City).
- Flags shared emails, missing key information, invalid email formats, and malformed CSV rows for review.
- Creates a cleaned CSV and an Excel report for each source file. The report contains Summary, Cleaned Data, Issues Found, and Duplicates Removed worksheets where applicable.

## Before processing a client file

1. Work from a copy of the client file.
2. Review `docs/CLIENT_INTAKE_CHECKLIST.txt` with the client.
3. Confirm the worksheet for XLSX files, field mappings, required fields, and the exact duplicate definition.
4. For a headerless file, configure `has_header=False` and its exact `column_order` in `run_pipeline.py`. The tool must not guess headers.
5. Review a small sample output before processing the full delivery.

## Quick start

Requirements: Python 3.10+ and `openpyxl`.

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python run_pipeline.py
```

Place client copies in `input/`. Results are written to `output/`; the source files remain unchanged. Generated outputs are intentionally excluded from version control.

## Included practice files

- `sample_customers.csv` and `sample_customers.xlsx` — basic examples.
- `no_header_test.csv` and `no_header_test.xlsx` — headerless examples that use explicit configuration.
- `client_stress_test.csv` — a realistic practice file containing an exact duplicate candidate, shared emails, missing details, an invalid email, similar names, and a malformed row.

## Safe defaults and current limits

- CustomerIDs are not automatically renumbered. Text IDs are preserved as supplied; Excel numeric IDs use their displayed value.
- Missing values are flagged, not fabricated.
- Shared email addresses and similar names are review flags, not proof of duplication.
- Fuzzy duplicate matching is not implemented.
- Supported input formats are CSV and XLSX; legacy XLS is not supported.
- Phone and date validation are intentionally limited until client-specific rules are supplied.

See `docs/KNOWN_LIMITATIONS.txt` for the full list of limits and `config/CLIENT_CONFIGURATION_EXAMPLE.py` for configuration guidance.

## Project layout

```text
Automated_Data_Quality_Tool/
├── input/       # source or practice files
├── output/      # generated delivery files (not committed)
├── docs/        # client intake and limitations
├── config/      # configuration examples
├── tests/       # automated tests
├── data_quality_engine.py
└── run_pipeline.py
```
