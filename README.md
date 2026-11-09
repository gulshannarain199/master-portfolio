# Master Portfolio

A collection of Python projects focused on data processing, practical automation, and network diagnostics.

## Featured projects

### 1. Automated Data Quality Tool

[Open project](04_Python_Practical_Projects/Automated_Data_Quality_Tool/)

A reusable Python tool for processing CSV and Excel files.

- Cleans and standardizes customer data.
- Preserves original CustomerIDs and source-row references.
- Detects exact duplicates using configured rules.
- Flags missing information, invalid emails, shared emails, and malformed CSV rows.
- Generates cleaned CSV files and Excel quality reports.
- Supports files with headers and explicitly configured headerless files.
- Includes automated tests and client documentation.

See the project's README for installation, configuration, workflow, and limitations.

### 2. Network Diagnostic Report Generator

[Open project](03_Network_Automation/)

A collection of Python network utilities and automation examples.

- Performs DNS resolution and TCP connectivity checks.
- Parses Cisco interface command output.
- Supports authorised multi-device SSH automation using Netmiko.
- Generates network diagnostic reports in JSON, CSV, and HTML formats.
- Includes offline demonstration mode and automated tests.

The offline demonstration uses sample Cisco output. It does not represent a live device diagnostic. See the project README for requirements and limitations.

## Other repository content

- `01_Python_Data_Science/` — Python learning and data science exercises.
- `03_Network_Automation/` — network diagnostic and automation tools.
- `04_Python_Practical_Projects/` — practical Python projects.

## Running a project

Each project has its own README and dependency requirements. Open the relevant project folder and follow its installation and usage instructions.

## Development approach

Projects are developed around practical problems, repeatable workflows, data integrity, testing, and clear documentation. Demonstrations and mocked tests are identified separately from real-world device or client testing.
