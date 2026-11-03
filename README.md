# Master Portfolio

Python projects in data handling, network utilities, and network automation. The featured project below demonstrates a safe, client-oriented workflow for cleaning CSV and Excel data.

## Featured project: Automated Data Quality Tool

[`04_Python_Practical_Projects/Automated_Data_Quality_Tool/`](04_Python_Practical_Projects/Automated_Data_Quality_Tool/) processes customer-style CSV and XLSX files without modifying the originals.

- Preserves source CustomerIDs, original columns, and source-row references.
- Removes only configured exact duplicates and retains an audit trail.
- Flags shared emails, missing fields, invalid email formats, malformed CSV rows, and other records needing review.
- Produces one cleaned CSV and one Excel quality report for every input file.
- Includes sample files, an intake checklist, configuration guidance, and automated tests.

Read the [project documentation](04_Python_Practical_Projects/Automated_Data_Quality_Tool/README.md) for the workflow, requirements, and limits.

## Repository structure

- `01_Python_Data_Science/` — Python fundamentals, data handling, APIs, and visualization exercises.
- `02_Python_Networking/` — small network utilities.
- `03_Network_Automation/` — automation scripts, including a DNS latency checker.
- `04_Python_Practical_Projects/` — client-oriented practical projects.

## Run a project

Clone the repository, then follow the README in the relevant project folder.

```bash
git clone https://github.com/gulshannarain199/master-portfolio.git
cd master-portfolio
cd 04_Python_Practical_Projects/Automated_Data_Quality_Tool
python -m pip install -r requirements.txt
python run_pipeline.py
```

## Data-handling approach

For data-cleaning work, original files are retained, IDs and row references are preserved, missing details are flagged rather than invented, and uncertain matches are reported for review instead of deleted automatically.
