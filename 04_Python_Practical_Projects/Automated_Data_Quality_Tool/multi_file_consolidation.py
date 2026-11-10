from __future__ import annotations

import csv
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import data_quality_engine as engine
from openpyxl import Workbook
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
REVIEW_FIELDS = ["ReviewGroupID", "MatchType", "RecordCount", "CustomerIDs",
                 "Names", "Emails", "SourceReferences", "ConflictingFields", "Details"]


def norm(value):
    return str(value or "").strip().casefold()


def record_ref(record):
    data = record["data"]
    return (f'{record["source_file"]} | {record["worksheet"]} | '
            f'row {record["original_row"]} | ID {data.get("customerid", "")}')


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
    data = record["data"]
    return {"SourceFile": record["source_file"],
            "SourceWorksheet": record["worksheet"],
            "OriginalRow": record["original_row"],
            "CustomerID": data.get("customerid", ""),
            "Name": data.get("name", ""), "Email": data.get("email", ""),
            "Issue": issue, "Details": details, "Severity": severity}


def _connected_components(records, predicate):
    """Group related records while retaining each source-row identity."""
    parent = list(range(len(records)))

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left, right):
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            if predicate(records[left], records[right]):
                union(left, right)

    grouped = defaultdict(list)
    for index, record in enumerate(records):
        grouped[find(index)].append(record)
    return [members for members in grouped.values() if len(members) > 1]


def _make_review_group(group_id, match_type, members, conflicts, details):
    members = sorted(members, key=lambda record: (
        record["source_file"], record["original_row"],
        norm(record["data"].get("customerid"))))

    def joined(field):
        values = []
        for record in members:
            value = str(record["data"].get(field) or "").strip()
            if value and value not in values:
                values.append(value)
        return " | ".join(values)

    return {
        "ReviewGroupID": group_id,
        "MatchType": match_type,
        "RecordCount": len(members),
        "CustomerIDs": joined("customerid"),
        "Names": joined("name"),
        "Emails": joined("email"),
        "SourceReferences": " || ".join(record_ref(record) for record in members),
        "ConflictingFields": ", ".join(conflicts) if conflicts else "None detected",
        "Details": details,
    }


def compare_records(records):
    issues = []
    valid = [record for record in records if not record["error"]]

    for record in records:
        data = record["data"]
        if record["error"]:
            issues.append(issue_row(
                record, "Invalid row structure", record["error"], "Error"))
            continue
        for field in ("customerid", "name", "email", "city"):
            if not str(data.get(field, "")).strip():
                issues.append(issue_row(
                    record, f"Missing {field.title()}",
                    f"The {field.title()} field is blank."))
        email = str(data.get("email", "")).strip()
        if email and not engine.EMAIL_PATTERN.fullmatch(email):
            issues.append(issue_row(
                record, "Invalid email format",
                f"The email address '{email}' does not appear valid."))

    by_email = defaultdict(list)
    for record in valid:
        email = norm(record["data"].get("email"))
        if email:
            by_email[email].append(record)

    for email, members in by_email.items():
        distinct_names = {
            norm(record["data"].get("name")) for record in members
            if norm(record["data"].get("name"))
        }
        if len(distinct_names) > 1:
            for record in members:
                issues.append(issue_row(
                    record, "Shared email address",
                    f"{email} is associated with different names; retain for client review."))

    groups = []

    exact_groups = _connected_components(
        valid,
        lambda left, right: all(
            norm(left["data"].get(field)) and
            norm(left["data"].get(field)) == norm(right["data"].get(field))
            for field in ("name", "email", "city")
        ),
    )
    for members in exact_groups:
        conflicts = [
            field for field in ("phone", "department")
            if len({norm(record["data"].get(field)) for record in members}) > 1
        ]
        details = (
            "Same name, email and city. All records retained pending client approval."
        )
        if conflicts:
            details += " Differences found in: " + ", ".join(conflicts) + "."
        groups.append(("Exact match", members, conflicts, details))

    possible_groups = _connected_components(
        valid,
        lambda left, right: (
            bool(norm(left["data"].get("name"))) and
            bool(norm(right["data"].get("name"))) and
            norm(left["data"].get("name")) != norm(right["data"].get("name")) and
            norm(left["data"].get("email")) != norm(right["data"].get("email")) and
            SequenceMatcher(
                None, norm(left["data"].get("name")),
                norm(right["data"].get("name"))
            ).ratio() >= 0.88
        ),
    )
    for members in possible_groups:
        similarities = []
        for index, left in enumerate(members):
            for right in members[index + 1:]:
                if norm(left["data"].get("email")) == norm(right["data"].get("email")):
                    continue
                ratio = SequenceMatcher(
                    None, norm(left["data"].get("name")),
                    norm(right["data"].get("name"))
                ).ratio()
                if ratio >= 0.88:
                    similarities.append(ratio)
        details = (
            "Related names appear at least 88% similar "
            f"(highest pair similarity {max(similarities):.0%}). "
            "Email addresses differ; human review required."
        )
        groups.append(("Possible name match", members, [], details))

    for email, members in by_email.items():
        distinct_names = {
            norm(record["data"].get("name")) for record in members
            if norm(record["data"].get("name"))
        }
        if len(distinct_names) > 1:
            conflicts = [
                field for field in ("name", "city", "phone", "department")
                if len({norm(record["data"].get(field)) for record in members}) > 1
            ]
            groups.append((
                "Shared-email conflict", members, conflicts,
                "The same email is associated with different record details. "
                "Neither source is preferred; preserve all records for review."
            ))

    review_rows = []
    for number, (kind, members, conflicts, details) in enumerate(groups, start=1):
        review_rows.append(_make_review_group(
            f"RG-{number:03d}", kind, members, conflicts, details))
    return issues, review_rows


def output_row(record):
    data = record["data"]
    return {"CustomerID": data.get("customerid", ""),
            "Name": data.get("name", ""), "Email": data.get("email", ""),
            "City": data.get("city", ""), "Phone": data.get("phone", ""),
            "Department": data.get("department", ""),
            "SourceFile": record["source_file"],
            "SourceWorksheet": record["worksheet"],
            "OriginalRow": record["original_row"]}


def write_csv(path, fields, rows):
    with Path(path).open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_report(path, records, issues, review_rows, sources):
    workbook = Workbook()
    summary = workbook.active
    summary.title = "Summary"

    counts = {
        "Exact-match groups": sum(row["MatchType"] == "Exact match" for row in review_rows),
        "Possible-name-match groups": sum(
            row["MatchType"] == "Possible name match" for row in review_rows),
        "Shared-email conflict groups": sum(
            row["MatchType"] == "Shared-email conflict" for row in review_rows),
    }
    unique_review_records = {
        reference
        for row in review_rows
        for reference in row["SourceReferences"].split(" || ")
    }

    summary.append(["Client Case Study 01 – Consolidation Summary"])
    summary.append(["Metric", "Count"])
    metrics = [
        ("Source files processed", len(sources)),
        ("Input records", len(records)),
        ("Consolidated records retained", len(records)),
        ("Records removed automatically", 0),
        ("Quality issue rows", len(issues)),
        *counts.items(),
        ("Total review groups", len(review_rows)),
        ("Unique records appearing in review groups", len(unique_review_records)),
        ("Status", "REVIEW REQUIRED" if issues or review_rows else "PASS"),
    ]
    for label, value in metrics:
        summary.append([label, value])
    summary.append([])
    summary.append(["Source file", "Worksheet", "Input records"])
    for source in sources:
        summary.append([
            source["source_file"], source["worksheet"], source["input_records"]])

    sheets = [
        ("Consolidated Data", OUTPUT_FIELDS, [output_row(record) for record in records]),
        ("Issues Found", ISSUE_FIELDS, issues),
        ("Duplicate Review", REVIEW_FIELDS, review_rows),
    ]
    for title, fields, rows in sheets:
        sheet = workbook.create_sheet(title)
        sheet.append(fields)
        for row in rows:
            sheet.append([row.get(field, "") for field in fields])

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(color="FFFFFF", bold=True)
    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        sheet.sheet_view.showGridLines = False
        if sheet.max_row > 1:
            sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for column in sheet.columns:
            letter = get_column_letter(column[0].column)
            longest = max((len(str(cell.value or "")) for cell in column), default=10)
            sheet.column_dimensions[letter].width = min(max(longest + 2, 14), 52)
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

    workbook.save(path)
    workbook.close()


def run_consolidation(package_dir=None, output_dir=None):
    default_package = Path(__file__).resolve().parents[2] / "Client_Case_01_Package"
    package = Path(package_dir) if package_dir else default_package
    destination = (
        Path(output_dir) if output_dir else
        Path(__file__).resolve().parent / "output" / "client_case_01"
    )
    destination.mkdir(parents=True, exist_ok=True)

    records, sources = load_sources(package)
    issues, review_rows = compare_records(records)

    outputs = {
        "cleaned_csv": destination / "client_case_01_consolidated.csv",
        "issues_csv": destination / "client_case_01_issues.csv",
        "duplicates_csv": destination / "client_case_01_duplicate_review.csv",
        "report_xlsx": destination / "client_case_01_quality_report.xlsx",
    }
    temporary = {
        key: path.with_name(path.stem + ".tmp" + path.suffix)
        for key, path in outputs.items()
    }
    backups, installed = {}, []

    try:
        write_csv(temporary["cleaned_csv"], OUTPUT_FIELDS,
                  [output_row(record) for record in records])
        write_csv(temporary["issues_csv"], ISSUE_FIELDS, issues)
        write_csv(temporary["duplicates_csv"], REVIEW_FIELDS, review_rows)
        write_report(temporary["report_xlsx"], records, issues, review_rows, sources)

        try:
            for key, final_path in outputs.items():
                if final_path.exists():
                    backup = final_path.with_name(final_path.name + ".bak")
                    if backup.exists():
                        backup.unlink()
                    final_path.replace(backup)
                    backups[key] = backup
            for key, temp_path in temporary.items():
                temp_path.replace(outputs[key])
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
        for temp_path in temporary.values():
            temp_path.unlink(missing_ok=True)
        raise

    category_counts = {
        "exact_match_groups": sum(row["MatchType"] == "Exact match" for row in review_rows),
        "possible_name_groups": sum(
            row["MatchType"] == "Possible name match" for row in review_rows),
        "shared_email_groups": sum(
            row["MatchType"] == "Shared-email conflict" for row in review_rows),
    }
    unique_records = {
        reference
        for row in review_rows
        for reference in row["SourceReferences"].split(" || ")
    }
    return {
        "source_files": len(sources), "input_records": len(records),
        "retained_records": len(records), "records_removed": 0,
        "issues": len(issues), "review_groups": len(review_rows),
        **category_counts,
        "unique_records_in_review_groups": len(unique_records),
        **{key: str(value) for key, value in outputs.items()},
    }


if __name__ == "__main__":
    for key, value in run_consolidation().items():
        print(f"{key}: {value}")
