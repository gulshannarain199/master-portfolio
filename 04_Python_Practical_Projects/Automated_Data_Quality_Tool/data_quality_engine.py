"""Reusable data-quality engine for CSV and XLSX files.

Headerless inputs require explicit configuration.
Original source files are never modified.
Cleaned outputs retain source columns and add an OriginalRow field.
"""

import csv
import uuid
import re
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_INPUT_FILE = BASE_DIR / "input" / "sample_customers.csv"


COLUMN_ALIASES = {
    "customerid": {
        "customerid", "customer id", "customer_id",
        "customer number", "customer no", "customer_no"
    },
    "name": {"name", "full name", "customer name", "fullname"},
    "email": {"email", "email address", "e-mail", "e-mail address"},
    "city": {"city", "town"},
    "phone": {"phone", "phone number", "mobile", "mobile number", "telephone"},
}

REQUIRED_COLUMNS = {"customerid", "name", "email", "city"}


EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+"
)


def normalize_header(value):
    return " ".join(str(value or "").strip().casefold().split())


def _canonical_mapping(headers, configured_mapping=None):
    normalized = [normalize_header(h) for h in headers]

    if any(not h for h in normalized):
        raise ValueError("Column names cannot be blank.")

    if len(set(normalized)) != len(normalized):
        raise ValueError("The input contains duplicate column names.")

    mapping = {}

    if configured_mapping:
        for canonical, source_name in configured_mapping.items():
            source = normalize_header(source_name)

            if source not in normalized:
                raise ValueError(
                    f"Configured column '{source_name}' for "
                    f"'{canonical}' was not found."
                )

            mapping[canonical] = source

    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in mapping:
            continue

        matches = [
            h for h in normalized
            if h in {normalize_header(a) for a in aliases}
        ]

        if len(matches) > 1:
            raise ValueError(
                f"Multiple columns match '{canonical}': {', '.join(matches)}"
            )

        if matches:
            mapping[canonical] = matches[0]

    missing = REQUIRED_COLUMNS - set(mapping)

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing))
        )

    return mapping


def _read_csv(
    path,
    *,
    has_header=True,
    column_order=None,
    column_mapping=None,
    encoding="utf-8-sig",
    delimiter=","
):
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter, strict=True)
        rows = list(reader)

    nonblank = [
        (idx, row)
        for idx, row in enumerate(rows, start=1)
        if row and any(str(v).strip() for v in row)
    ]

    if not nonblank:
        raise ValueError("The CSV file is empty.")

    if has_header:
        _, headers = nonblank[0]
        headers = [str(v).strip() for v in headers]
        mapping = _canonical_mapping(headers, column_mapping)
        data_rows = nonblank[1:]

    else:
        if not column_order:
            raise ValueError(
                "Headerless CSV requires an explicit column_order."
            )

        headers = [str(v).strip() for v in column_order]
        mapping = _canonical_mapping(headers, column_mapping)
        data_rows = nonblank

    records = []

    for row_no, row in data_rows:
        if len(row) != len(headers):
            records.append({
                "original_row": row_no,
                "raw": None,
                "data": None,
                "error": (
                    f"Expected {len(headers)} fields "
                    f"but found {len(row)}."
                )
            })
            continue

        raw = {
            str(headers[i]).strip():
            (row[i] if row[i] is not None else "")
            for i in range(len(headers))
        }

        normalized_raw = {
            normalize_header(k): str(v).strip()
            for k, v in raw.items()
        }

        data = {
            canonical: normalized_raw.get(source, "")
            for canonical, source in mapping.items()
        }

        records.append({
            "original_row": row_no,
            "raw": raw,
            "data": data,
            "error": None
        })

    if not records:
        raise ValueError("The CSV contains no data records.")

    return headers, mapping, records


def _excel_display_value(cell):
    value = cell.value

    if (
        isinstance(value, int)
        and cell.number_format
        and re.fullmatch(r"0+", cell.number_format)
    ):
        return str(value).zfill(len(cell.number_format))

    return "" if value is None else str(value)


def _read_xlsx(
    path,
    *,
    has_header=True,
    column_order=None,
    column_mapping=None,
    sheet_name=None,
    sheet_index=0
):
    workbook = load_workbook(path, read_only=True, data_only=True)

    try:
        if sheet_name is not None:
            if sheet_name not in workbook.sheetnames:
                raise ValueError(
                    f"Worksheet '{sheet_name}' was not found."
                )

            sheet = workbook[sheet_name]

        else:
            if sheet_index < 0 or sheet_index >= len(workbook.worksheets):
                raise ValueError(
                    f"Worksheet index {sheet_index} is out of range."
                )

            sheet = workbook.worksheets[sheet_index]

        rows = []

        for row in sheet.iter_rows():
            values = [_excel_display_value(cell) for cell in row]

            if any(v.strip() for v in values):
                rows.append((row[0].row, values))

        if not rows:
            raise ValueError("The Excel worksheet is empty.")

        if has_header:
            _, headers = rows[0]
            headers = [str(v).strip() for v in headers]
            mapping = _canonical_mapping(headers, column_mapping)
            data_rows = rows[1:]

        else:
            if not column_order:
                raise ValueError(
                    "Headerless Excel requires an explicit column_order."
                )

            headers = [str(v).strip() for v in column_order]
            mapping = _canonical_mapping(headers, column_mapping)
            data_rows = rows

        records = []

        for row_no, values in data_rows:
            if len(values) < len(headers):
                values += [""] * (len(headers) - len(values))

            if (
                len(values) > len(headers)
                and any(v for v in values[len(headers):])
            ):
                records.append({
                    "original_row": row_no,
                    "raw": None,
                    "data": None,
                    "error": (
                        f"Expected {len(headers)} columns "
                        f"but found {len(values)}."
                    )
                })
                continue

            values = values[:len(headers)]

            raw = {
                headers[i]: values[i]
                for i in range(len(headers))
            }

            normalized_raw = {
                normalize_header(k): str(v).strip()
                for k, v in raw.items()
            }

            data = {
                canonical: normalized_raw.get(source, "")
                for canonical, source in mapping.items()
            }

            records.append({
                "original_row": row_no,
                "raw": raw,
                "data": data,
                "error": None
            })

        if not records:
            raise ValueError(
                "The Excel worksheet contains no data records."
            )

        return headers, mapping, records

    finally:
        workbook.close()


def read_input_file(
    input_file,
    *,
    has_header=True,
    column_order=None,
    column_mapping=None,
    sheet_name=None,
    sheet_index=0,
    delimiter=",",
    encoding="utf-8-sig"
):
    path = Path(input_file)
    suffix = path.suffix.casefold()

    if suffix == ".csv":
        return _read_csv(
            path,
            has_header=has_header,
            column_order=column_order,
            column_mapping=column_mapping,
            encoding=encoding,
            delimiter=delimiter
        )

    if suffix == ".xlsx":
        return _read_xlsx(
            path,
            has_header=has_header,
            column_order=column_order,
            column_mapping=column_mapping,
            sheet_name=sheet_name,
            sheet_index=sheet_index
        )

    raise ValueError(
        f"Unsupported file type '{path.suffix}'. "
        "Supported formats: .csv and .xlsx"
    )


def inspect_records(records, *, duplicate_keys=("name", "email", "city")):
    issues = []
    duplicate_rows = []
    seen = {}

    for item in records:
        data = item["data"]
        row = item["original_row"]

        if data is None:
            issues.append({
                "original_row": row,
                "issue": "Invalid row structure",
                "details": item["error"],
                "severity": "Error"
            })
            continue

        for field in REQUIRED_COLUMNS:
            if not str(data.get(field, "")).strip():
                issues.append({
                    "original_row": row,
                    "issue": f"Missing {field.title()}",
                    "details": f"The {field.title()} field is blank.",
                    "severity": "Review"
                })

        email = str(data.get("email", "")).strip()

        if email and not EMAIL_PATTERN.fullmatch(email):
            issues.append({
                "original_row": row,
                "issue": "Invalid email format",
                "details": (
                    f"The email address '{email}' does not appear "
                    "to be valid. Review it."
                ),
                "severity": "Review"
            })

        key_values = [
            str(data.get(k, "")).strip()
            for k in duplicate_keys
        ]

        if all(key_values):
            key = tuple(v.casefold() for v in key_values)

            if key in seen:
                duplicate_rows.append({
                    "original_row": row,
                    "matching_row": seen[key],
                    "customer_id": data.get("customerid", ""),
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "city": data.get("city", "")
                })

            else:
                seen[key] = row

    email_groups = defaultdict(list)

    for item in records:
        data = item["data"]

        if data is not None and str(data.get("email", "")).strip():
            email_groups[
                str(data["email"]).strip().casefold()
            ].append(item)

    for email, items in email_groups.items():
        names = {
            str(i["data"].get("name", "")).strip().casefold()
            for i in items
            if str(i["data"].get("name", "")).strip()
        }

        if len(names) > 1:
            for item in items:
                issues.append({
                    "original_row": item["original_row"],
                    "issue": "Shared email address",
                    "details": (
                        f"{item['data'].get('email', '')} is used "
                        "by different names. Review it."
                    ),
                    "severity": "Review"
                })

    return issues, duplicate_rows


def clean_records(records, duplicate_rows):
    duplicate_numbers = {
        d["original_row"]
        for d in duplicate_rows
    }

    retained = []
    removed = []

    for item in records:
        if item["data"] is None:
            continue

        (
            removed if item["original_row"] in duplicate_numbers
            else retained
        ).append(item)

    return retained, removed


def validate_results(records, retained, removed):
    valid = sum(
        1 for r in records
        if r["data"] is not None
    )

    if valid != len(retained) + len(removed):
        raise ValueError("Count validation failed.")

    return valid


def _output_headers(headers):
    return ["OriginalRow"] + list(headers)


def write_cleaned_csv(path, headers, retained, mapping=None):
    """Write cleaned CSV data while preserving original input columns."""

    canonical_by_source = {
        source: canonical
        for canonical, source in (mapping or {}).items()
    }

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_output_headers(headers))

        for item in retained:
            raw = item["raw"] or {}
            data = item["data"] or {}

            cleaned_values = []

            for header in headers:
                normalized_header = normalize_header(header)
                canonical = canonical_by_source.get(normalized_header)

                value = raw.get(header, "")

                if canonical == "customerid":
                    value = str(value)

                elif canonical == "name":
                    value = str(data.get("name", "")).strip().title()

                elif canonical == "email":
                    value = str(data.get("email", "")).strip().lower()

                else:
                    value = str(value).strip()

                cleaned_values.append(value)

            writer.writerow(
                [item["original_row"]] + cleaned_values
            )


def _style_sheet(ws):
    """Apply consistent, readable business-report formatting."""
    navy = "1F4E78"
    light_blue = "D9EAF7"
    alternate = "F3F6FA"
    white = "FFFFFF"
    border_color = "D9E2F3"

    ws.freeze_panes = "A2"

    if ws.max_row and ws.max_column:
        ws.auto_filter.ref = ws.dimensions

    ws.sheet_view.showGridLines = False
    ws.row_dimensions[1].height = 28

    for cell in ws[1]:
        cell.font = Font(bold=True, color=white, size=11)
        cell.fill = PatternFill(fill_type="solid", fgColor=navy)
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    for row_number in range(2, ws.max_row + 1):
        ws.row_dimensions[row_number].height = 30
        for cell in ws[row_number]:
            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True,
            )
            if row_number % 2 == 0:
                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor=alternate,
                )

    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        width = max(
            (len(str(cell.value or "")) for cell in col),
            default=10,
        )
        ws.column_dimensions[letter].width = min(
            max(width + 3, 14),
            60,
        )

    thin_border = Border(
        bottom=Side(style="hair", color=border_color)
    )
    for row in ws.iter_rows():
        for cell in row:
            cell.border = thin_border

    if ws.title == "Issues Found":
        severity_colors = {
            "error": "F4CCCC",
            "review": "FFF2CC",
            "warning": "FCE4D6",
        }
        for row in range(2, ws.max_row + 1):
            severity = str(ws.cell(row, 4).value or "").strip().lower()
            fill = severity_colors.get(severity)
            if fill:
                for cell in ws[row]:
                    cell.fill = PatternFill(
                        fill_type="solid",
                        fgColor=fill,
                    )

def write_excel_report(
    path,
    headers,
    records,
    retained,
    removed,
    issues,
    duplicate_rows,
    mapping=None
):
    """Write the Excel report with the same standardisation as the CSV output."""

    canonical_by_source = {
        source: canonical
        for canonical, source in (mapping or {}).items()
    }

    wb = Workbook()

    summary = wb.active
    summary.title = "Summary"

    summary.append(["Data Quality Report", ""])
    summary.append(["Input records", len(records)])
    summary.append([
        "Structurally valid records",
        sum(r["data"] is not None for r in records)
    ])
    summary.append(["Records retained", len(retained)])
    summary.append(["Exact duplicates removed", len(removed)])
    summary.append(["Issue occurrences", len(issues)])
    summary.append([
        "Count validation",
        "PASS" if len(retained) + len(removed) ==
        sum(r["data"] is not None for r in records)
        else "FAIL"
    ])

    cleaned = wb.create_sheet("Cleaned Data")
    cleaned.append(_output_headers(headers))

    for item in retained:
        raw = item["raw"] or {}
        data = item["data"] or {}
        cleaned_values = []

        for header in headers:
            normalized_header = normalize_header(header)
            canonical = canonical_by_source.get(normalized_header)
            value = raw.get(header, "")

            if canonical == "customerid":
                value = str(value)

            elif canonical == "name":
                value = str(data.get("name", "")).strip().title()

            elif canonical == "email":
                value = str(data.get("email", "")).strip().lower()

            else:
                value = str(value).strip()

            cleaned_values.append(value)

        cleaned.append(
            [item["original_row"]] + cleaned_values
        )

    issue_ws = wb.create_sheet("Issues Found")
    issue_ws.append([
        "Original Row",
        "Issue",
        "Details",
        "Severity"
    ])

    for issue in issues:
        issue_ws.append([
            issue["original_row"],
            issue["issue"],
            issue["details"],
            issue["severity"]
        ])

    dup_ws = wb.create_sheet("Duplicates Removed")
    dup_ws.append([
        "Original Row",
        "Matching Original Row",
        "CustomerID",
        "Name",
        "Email",
        "City"
    ])

    for d in duplicate_rows:
        dup_ws.append([
            d["original_row"],
            d["matching_row"],
            d["customer_id"],
            d["name"],
            d["email"],
            d["city"]
        ])

    for ws in wb.worksheets:
        _style_sheet(ws)

    summary["A1"].font = Font(
        bold=True,
        size=16,
        color="FFFFFF",
    )
    summary["A1"].fill = PatternFill(
        fill_type="solid",
        fgColor="17365D",
    )
    summary["A1"].alignment = Alignment(
        vertical="center",
        horizontal="left",
    )
    summary.row_dimensions[1].height = 36
    summary.column_dimensions["A"].width = 34
    summary.column_dimensions["B"].width = 22

    for row in range(2, summary.max_row + 1):
        label = summary.cell(row, 1)
        value = summary.cell(row, 2)

        label.font = Font(bold=True, color="1F1F1F")
        label.fill = PatternFill(
            fill_type="solid",
            fgColor="D9EAF7",
        )
        value.font = Font(bold=True, size=12, color="17365D")
        value.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        summary.row_dimensions[row].height = 25

    status = str(summary["B7"].value or "").upper()
    summary["B7"].fill = PatternFill(
        fill_type="solid",
        fgColor="E2F0D9" if status == "PASS" else "F4CCCC",
    )
    summary["B7"].font = Font(
        bold=True,
        color="38761D" if status == "PASS" else "990000",
        size=12,
    )

    wb.save(path)


def process_file(
    input_file,
    *,
    has_header=True,
    column_order=None,
    column_mapping=None,
    sheet_name=None,
    sheet_index=0,
    delimiter=",",
    encoding="utf-8-sig",
    duplicate_keys=("name", "email", "city"),
    output_dir=None
):
    input_path = Path(input_file)

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    destination = Path(output_dir) if output_dir else OUTPUT_DIR
    destination.mkdir(parents=True, exist_ok=True)

    headers, mapping, records = read_input_file(
        input_path,
        has_header=has_header,
        column_order=column_order,
        column_mapping=column_mapping,
        sheet_name=sheet_name,
        sheet_index=sheet_index,
        delimiter=delimiter,
        encoding=encoding
    )

    issues, duplicates = inspect_records(
        records,
        duplicate_keys=duplicate_keys
    )

    retained, removed = clean_records(records, duplicates)

    validate_results(records, retained, removed)

    source_tag = (
        f"{input_path.stem}_{input_path.suffix.lstrip('.').casefold()}"
    )

    cleaned_csv = destination / f"cleaned_{source_tag}.csv"
    report_xlsx = destination / f"data_quality_report_{source_tag}.xlsx"

    temp_csv = cleaned_csv.with_name(
        cleaned_csv.stem + ".tmp" + cleaned_csv.suffix
    )

    temp_xlsx = report_xlsx.with_name(
        report_xlsx.stem + ".tmp" + report_xlsx.suffix
    )

    try:
        write_cleaned_csv(
            temp_csv,
            headers,
            retained,
            mapping=mapping
        )

        write_excel_report(
            temp_xlsx,
            headers,
            records,
            retained,
            removed,
            issues,
            duplicates,
            mapping=mapping
        )

        token = uuid.uuid4().hex
        csv_backup = cleaned_csv.with_name(
            f".{cleaned_csv.name}.{token}.bak"
        )
        xlsx_backup = report_xlsx.with_name(
            f".{report_xlsx.name}.{token}.bak"
        )

        csv_backed_up = False
        xlsx_backed_up = False
        csv_installed = False
        xlsx_installed = False

        try:
            if cleaned_csv.exists():
                cleaned_csv.replace(csv_backup)
                csv_backed_up = True

            if report_xlsx.exists():
                report_xlsx.replace(xlsx_backup)
                xlsx_backed_up = True

            temp_csv.replace(cleaned_csv)
            csv_installed = True

            temp_xlsx.replace(report_xlsx)
            xlsx_installed = True

        except Exception:
            if csv_installed:
                cleaned_csv.unlink(missing_ok=True)
            if xlsx_installed:
                report_xlsx.unlink(missing_ok=True)

            if csv_backed_up and csv_backup.exists():
                csv_backup.replace(cleaned_csv)
            if xlsx_backed_up and xlsx_backup.exists():
                xlsx_backup.replace(report_xlsx)

            raise

        if csv_backup.exists():
            csv_backup.unlink()
        if xlsx_backup.exists():
            xlsx_backup.unlink()

    except Exception:
        temp_csv.unlink(missing_ok=True)
        temp_xlsx.unlink(missing_ok=True)
        raise

    return {
        "input_file": input_path.name,
        "input_records": len(records),
        "retained": len(retained),
        "duplicates_removed": len(removed),
        "issues": len(issues),
        "cleaned_csv": str(cleaned_csv),
        "excel_report": str(report_xlsx),
        "column_mapping": mapping
    }


def main(input_file=DEFAULT_INPUT_FILE, **config):
    try:
        result = process_file(input_file, **config)

        print(
            f"Processed {result['input_file']}: "
            f"{result['input_records']} input, "
            f"{result['retained']} retained, "
            f"{result['duplicates_removed']} duplicates removed, "
            f"{result['issues']} issues."
        )

        print(f"Cleaned CSV: {result['cleaned_csv']}")
        print(f"Excel report: {result['excel_report']}")

        return True

    except (
        OSError,
        UnicodeError,
        csv.Error,
        ValueError,
        KeyError
    ) as exc:
        print(
            f"ERROR processing {Path(input_file).name}: {exc}"
        )
        return False


if __name__ == "__main__":
    if not main():
        raise SystemExit(1)