#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
PROJECT = ROOT / "04_Python_Practical_Projects" / "Automated_Data_Quality_Tool"
PACKAGE = ROOT / "Client_Case_01_Package"

if not PROJECT.is_dir() or not PACKAGE.is_dir():
    raise SystemExit("Run this script from the master-portfolio repository root; required project/package folders were not found.")

files = {
"multi_file_consolidation.py": r"""
from __future__ import annotations
import csv
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
import data_quality_engine as engine
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SOURCE_CONFIG = {
    "Client_Case_01_Input_A_Customer_Master.xlsx": {
        "sheet_name": "Client Records",
        "column_mapping": {
            "customerid": "Customer ID", "name": "Full Name",
            "email": "Email Address", "city": "Town",
            "phone": "Mobile Number", "department": "Department",
        },
    },
    "Client_Case_01_Input_B_Regional_Records.xlsx": {
        "sheet_name": "Client Records",
        "column_mapping": {
            "customerid": "Client Ref", "name": "Client Name",
            "email": "Email", "city": "Region",
            "phone": "Phone", "department": "Team",
        },
    },
}
OUTPUT_FIELDS = ["CustomerID", "Name", "Email", "City", "Phone",
                 "Department", "SourceFile", "SourceWorksheet", "OriginalRow"]
ISSUE_FIELDS = ["SourceFile", "SourceWorksheet", "OriginalRow", "CustomerID",
                "Name", "Email", "Issue", "Details", "Severity"]
DUP_FIELDS = ["MatchType", "SourceFileA", "WorksheetA", "RowA", "CustomerIDA",
              "SourceFileB", "WorksheetB", "RowB", "CustomerIDB",
              "NameA", "NameB", "EmailA", "EmailB", "Details"]

def norm(value):
    return str(value or "").strip().casefold()

def load_sources(package):
    records, summaries = [], []
    for filename, config in SOURCE_CONFIG.items():
        path = Path(package) / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing required workbook: {path}")
        _, mapping, rows = engine.read_input_file(
            path, has_header=True, column_mapping=config["column_mapping"],
            sheet_name=config["sheet_name"])
        for item in rows:
            data = item["data"]
            if data is None:
                canonical = {}
                error = item.get("error") or "Invalid row structure"
            else:
                canonical = {
                    "customerid": str(data.get("customerid") or "").strip(),
                    "name": str(data.get("name") or "").strip().title(),
                    "email": str(data.get("email") or "").strip().lower(),
                    "city": str(data.get("city") or "").strip(),
                    "phone": str(data.get("phone") or "").strip(),
                    "department": str(data.get("department") or "").strip(),
                }
                error = None
            records.append({
                "source_file": filename, "worksheet": config["sheet_name"],
                "original_row": item["original_row"], "data": canonical,
                "error": error,
            })
        summaries.append({"source_file": filename,
                          "worksheet": config["sheet_name"],
                          "input_records": len(rows), "mapping": mapping})
    return records, summaries

def issue_row(record, issue, details, severity="Review"):
    d = record["data"]
    return {"SourceFile": record["source_file"],
            "SourceWorksheet": record["worksheet"],
            "OriginalRow": record["original_row"],
            "CustomerID": d.get("customerid", ""),
            "Name": d.get("name", ""), "Email": d.get("email", ""),
            "Issue": issue, "Details": details, "Severity": severity}

def duplicate_row(kind, a, b, details):
    x, y = a["data"], b["data"]
    return {"MatchType": kind, "SourceFileA": a["source_file"],
            "WorksheetA": a["worksheet"], "RowA": a["original_row"],
            "CustomerIDA": x.get("customerid", ""),
            "SourceFileB": b["source_file"], "WorksheetB": b["worksheet"],
            "RowB": b["original_row"], "CustomerIDB": y.get("customerid", ""),
            "NameA": x.get("name", ""), "NameB": y.get("name", ""),
            "EmailA": x.get("email", ""), "EmailB": y.get("email", ""),
            "Details": details}

def compare_records(records):
    issues, candidates = [], []
    valid = [r for r in records if not r["error"]]
    for r in records:
        d = r["data"]
        if r["error"]:
            issues.append(issue_row(r, "Invalid row structure", r["error"], "Error"))
            continue
        for field in ("customerid", "name", "email", "city"):
            if not str(d.get(field, "")).strip():
                issues.append(issue_row(r, f"Missing {field.title()}",
                                        f"The {field.title()} field is blank."))
        email = str(d.get("email", "")).strip()
        if email and not engine.EMAIL_PATTERN.fullmatch(email):
            issues.append(issue_row(r, "Invalid email format",
                                    f"The email address '{email}' does not appear valid."))

    by_email = defaultdict(list)
    for r in valid:
        email = norm(r["data"].get("email"))
        if email:
            by_email[email].append(r)
    for email, group in by_email.items():
        names = {norm(r["data"].get("name")) for r in group
                 if norm(r["data"].get("name"))}
        if len(names) > 1:
            for r in group:
                issues.append(issue_row(
                    r, "Shared email address",
                    f"{email} is associated with different names; retain for client review."))

    # Exact candidates are reported, not automatically removed.
    seen = {}
    for r in valid:
        d = r["data"]
        key = tuple(norm(d.get(k)) for k in ("name", "email", "city"))
        if all(key):
            if key in seen:
                candidates.append(duplicate_row(
                    "Exact match", seen[key], r,
                    "Same name, email and city. Both records retained pending client approval."))
            else:
                seen[key] = r

    # Fuzzy-name candidates only: no automatic merging.
    named = [r for r in valid if norm(r["data"].get("name"))]
    for i, a in enumerate(named):
        for b in named[i + 1:]:
            x, y = a["data"], b["data"]
            if norm(x.get("name")) == norm(y.get("name")):
                continue
            if norm(x.get("email")) == norm(y.get("email")):
                continue
            ratio = SequenceMatcher(None, norm(x.get("name")),
                                    norm(y.get("name"))).ratio()
            if ratio >= 0.88:
                candidates.append(duplicate_row(
                    "Possible name match", a, b,
                    f"Names are {ratio:.0%} similar but email addresses differ. Human review required."))

    # Same email, different values: preserve both source records and show conflict.
    for group in by_email.values():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                differences = [f for f in ("name", "city", "phone", "department")
                               if norm(a["data"].get(f)) != norm(b["data"].get(f))]
                if differences:
                    candidates.append(duplicate_row(
                        "Shared-email conflict", a, b,
                        "Different values in: " + ", ".join(differences) +
                        ". Neither source is preferred; preserve both for review."))
    return issues, candidates

def output_row(r):
    d = r["data"]
    return {"CustomerID": d.get("customerid", ""), "Name": d.get("name", ""),
            "Email": d.get("email", ""), "City": d.get("city", ""),
            "Phone": d.get("phone", ""), "Department": d.get("department", ""),
            "SourceFile": r["source_file"], "SourceWorksheet": r["worksheet"],
            "OriginalRow": r["original_row"]}

def write_csv(path, fields, rows):
    with Path(path).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def write_report(path, records, issues, candidates, sources):
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Client Case Study 01 – Consolidation Summary"])
    ws.append(["Metric", "Count"])
    ws.append(["Source files processed", len(sources)])
    ws.append(["Input records", len(records)])
    ws.append(["Consolidated records retained", len(records)])
    ws.append(["Records removed automatically", 0])
    ws.append(["Quality issues", len(issues)])
    ws.append(["Duplicate / possible-match candidates", len(candidates)])
    ws.append(["Status", "REVIEW REQUIRED" if issues or candidates else "PASS"])
    ws.append([])
    ws.append(["Source file", "Worksheet", "Input records"])
    for s in sources:
        ws.append([s["source_file"], s["worksheet"], s["input_records"]])

    for title, fields, rows in (
        ("Consolidated Data", OUTPUT_FIELDS, [output_row(r) for r in records]),
        ("Issues Found", ISSUE_FIELDS, issues),
        ("Duplicate Review", DUP_FIELDS, candidates),
    ):
        sh = wb.create_sheet(title)
        sh.append(fields)
        for row in rows:
            sh.append([row.get(field, "") for field in fields])

    fill = PatternFill("solid", fgColor="17365D")
    font = Font(color="FFFFFF", bold=True)
    for sh in wb.worksheets:
        sh.freeze_panes = "A2"
        sh.sheet_view.showGridLines = False
        if sh.max_row > 1:
            sh.auto_filter.ref = sh.dimensions
        for cell in sh[1]:
            cell.fill, cell.font = fill, font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for col in sh.columns:
            letter = get_column_letter(col[0].column)
            longest = max((len(str(c.value or "")) for c in col), default=10)
            sh.column_dimensions[letter].width = min(max(longest + 2, 14), 48)
        for row in sh.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)
    wb.close()

def run_consolidation(package_dir=None, output_dir=None):
    default_package = Path(__file__).resolve().parents[2] / "Client_Case_01_Package"
    package = Path(package_dir) if package_dir else default_package
    dest = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "output" / "client_case_01"
    dest.mkdir(parents=True, exist_ok=True)
    records, sources = load_sources(package)
    issues, candidates = compare_records(records)
    outputs = {
        "cleaned_csv": dest / "client_case_01_consolidated.csv",
        "issues_csv": dest / "client_case_01_issues.csv",
        "duplicates_csv": dest / "client_case_01_duplicate_review.csv",
        "report_xlsx": dest / "client_case_01_quality_report.xlsx",
    }
    temps = {
        "cleaned_csv": dest / "client_case_01_consolidated.tmp.csv",
        "issues_csv": dest / "client_case_01_issues.tmp.csv",
        "duplicates_csv": dest / "client_case_01_duplicate_review.tmp.csv",
        "report_xlsx": dest / "client_case_01_quality_report.tmp.xlsx",
    }
    backups, installed = {}, []
    try:
        write_csv(temps["cleaned_csv"], OUTPUT_FIELDS, [output_row(r) for r in records])
        write_csv(temps["issues_csv"], ISSUE_FIELDS, issues)
        write_csv(temps["duplicates_csv"], DUP_FIELDS, candidates)
        write_report(temps["report_xlsx"], records, issues, candidates, sources)
        try:
            for key, final in outputs.items():
                if final.exists():
                    backup = final.with_name(final.name + ".bak")
                    if backup.exists():
                        backup.unlink()
                    final.replace(backup)
                    backups[key] = backup
            for key, temp in temps.items():
                temp.replace(outputs[key])
                installed.append(key)
        except Exception:
            for key in installed:
                outputs[key].unlink(missing_ok=True)
            for key, backup in backups.items():
                if backup.exists():
                    backup.replace(outputs[key])
            raise
        for backup in backups.values():
            backup.unlink(missing_ok=True)
    except Exception:
        for temp in temps.values():
            temp.unlink(missing_ok=True)
        raise
    return {"source_files": len(sources), "input_records": len(records),
            "retained_records": len(records), "records_removed": 0,
            "issues": len(issues), "duplicate_candidates": len(candidates),
            **{k: str(v) for k, v in outputs.items()}}

if __name__ == "__main__":
    for key, value in run_consolidation().items():
        print(f"{key}: {value}")
""",
"tests/test_multi_file_consolidation.py": r"""
import tempfile
import unittest
from pathlib import Path
from openpyxl import load_workbook
import multi_file_consolidation as consolidation

class TestMultiFileConsolidation(unittest.TestCase):
    def test_case_study_workbooks_are_consolidated(self):
        package = Path(__file__).resolve().parents[3] / "Client_Case_01_Package"
        if not package.exists():
            self.skipTest("Case study input package not available.")
        with tempfile.TemporaryDirectory() as temp:
            result = consolidation.run_consolidation(package, temp)
            self.assertEqual(result["source_files"], 2)
            self.assertEqual(result["input_records"], 26)
            self.assertEqual(result["retained_records"], 26)
            self.assertEqual(result["records_removed"], 0)
            for key in ("cleaned_csv", "issues_csv", "duplicates_csv", "report_xlsx"):
                self.assertTrue(Path(result[key]).is_file())
            wb = load_workbook(result["report_xlsx"], read_only=True)
            self.assertEqual(wb["Consolidated Data"].max_row, 27)
            self.assertIn("Duplicate Review", wb.sheetnames)
            self.assertIn("Issues Found", wb.sheetnames)
            wb.close()

    def test_row_numbers_are_scoped_to_source_file(self):
        def rec(source, cid, name, email, city):
            return {"source_file": source, "worksheet": "Sheet1", "original_row": 2,
                    "data": {"customerid": cid, "name": name, "email": email,
                             "city": city, "phone": "", "department": ""}, "error": None}
        a = rec("A.xlsx", "A1", "Alex Brown", "alex@example.com", "Port Louis")
        b = rec("B.xlsx", "B1", "Jamie Brown", "jamie@example.com", "Curepipe")
        _, matches = consolidation.compare_records([a, b])
        self.assertEqual(matches, [])

if __name__ == "__main__":
    unittest.main()
""",
"run_client_case_01.py": r"""
import subprocess
import sys
from pathlib import Path
project = Path(__file__).resolve().parent
raise SystemExit(subprocess.run(
    [sys.executable, "multi_file_consolidation.py"], cwd=project
).returncode)
""",
}

for relative, content in files.items():
    target = PROJECT / relative
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    print("Created:", target.relative_to(ROOT))

print("\nRunning all existing and new tests...")
test_run = subprocess.run(
    [sys.executable, "-m", "pytest", "-q"], cwd=PROJECT, text=True
)
if test_run.returncode:
    raise SystemExit("TESTS FAILED. Files are left for diagnosis; no commit or push made.")

print("\nRunning Client Case Study 01...")
case_run = subprocess.run(
    [sys.executable, "run_client_case_01.py"], cwd=PROJECT, text=True
)
if case_run.returncode:
    raise SystemExit("CASE STUDY RUN FAILED. No commit or push made.")

print("\nSUCCESS. Tests and case study completed.")
print("Outputs are in Automated_Data_Quality_Tool/output/client_case_01/")
print("No existing source files were overwritten. No Git commit or push was made.")
