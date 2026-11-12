"""Analyse Cisco 'show ip interface brief' output without device access."""

import argparse
import csv
import html
import json
from pathlib import Path


def parse_interface_output(raw_output):
    """Return all recognizable interface rows, not only interfaces that are up."""
    interfaces = []
    for line_number, line in enumerate(raw_output.splitlines(), start=1):
        parts = line.split()
        if len(parts) < 6 or parts[0].lower() == "interface":
            continue
        if set(line.strip()) <= {"-", "="}:
            continue
        interface_name, ip_address = parts[0], parts[1]
        status = " ".join(parts[4:-1]).strip()
        protocol = parts[-1].strip()
        if not status or not protocol:
            continue
        if status.lower() == "up" and protocol.lower() == "up":
            finding = "OPERATIONAL"
            recommendation = "No action indicated by this interface summary."
        elif "administratively down" in status.lower():
            finding = "ADMINISTRATIVELY_DOWN"
            recommendation = "Confirm whether the interface is intentionally shut down."
        else:
            finding = "NOT_OPERATIONAL"
            recommendation = "Review the interface, cabling, peer device, VLAN, and relevant configuration."
        interfaces.append({
            "source_line": line_number, "interface": interface_name,
            "ip_address": ip_address, "status": status, "protocol": protocol,
            "finding": finding, "recommendation": recommendation,
        })
    return interfaces


def build_audit(raw_output, source_name="client-supplied-output.txt"):
    interfaces = parse_interface_output(raw_output)
    return {
        "source_file": source_name,
        "command": "show ip interface brief",
        "scope_note": "This report analyses supplied command output only. It does not connect to or modify network devices, and findings are not proof of root cause.",
        "summary": {
            "interfaces_found": len(interfaces),
            "operational": sum(x["finding"] == "OPERATIONAL" for x in interfaces),
            "administratively_down": sum(x["finding"] == "ADMINISTRATIVELY_DOWN" for x in interfaces),
            "not_operational": sum(x["finding"] == "NOT_OPERATIONAL" for x in interfaces),
        },
        "interfaces": interfaces,
    }


def write_reports(audit, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "interface_audit.json"
    csv_path = output_dir / "interface_audit.csv"
    html_path = output_dir / "interface_audit.html"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    fields = ["source_line", "interface", "ip_address", "status", "protocol", "finding", "recommendation"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit["interfaces"])
    summary_rows = "".join(f"<li>{html.escape(key.replace('_', ' ').title())}: {value}</li>" for key, value in audit["summary"].items())
    table_rows = "".join("<tr>" + "".join(f"<td>{html.escape(str(item[field]))}</td>" for field in fields) + "</tr>" for item in audit["interfaces"])
    headings = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Cisco Interface Audit</title>
<style>body{{font-family:Arial,sans-serif;margin:2rem;color:#222}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:.55rem;text-align:left}}th{{background:#eee}}.note{{padding:.8rem;background:#f4f4f4}}</style>
</head><body><h1>Cisco Interface Audit</h1>
<p>Source: {html.escape(audit['source_file'])}</p><p>Command: {html.escape(audit['command'])}</p>
<p class="note">{html.escape(audit['scope_note'])}</p><h2>Summary</h2><ul>{summary_rows}</ul>
<h2>Interface findings</h2><table><thead><tr>{headings}</tr></thead><tbody>{table_rows}</tbody></table>
</body></html>"""
    html_path.write_text(page, encoding="utf-8")
    return json_path, csv_path, html_path


def main():
    parser = argparse.ArgumentParser(description="Audit a client-supplied Cisco show ip interface brief text file.")
    parser.add_argument("--input", required=True, help="Path to the supplied command-output text file")
    parser.add_argument("--output-dir", default="interface_audit_output", help="Directory for JSON, CSV and HTML reports")
    args = parser.parse_args()
    input_path = Path(args.input).expanduser()
    if not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")
    audit = build_audit(input_path.read_text(encoding="utf-8"), input_path.name)
    for path in write_reports(audit, args.output_dir):
        print(f"Report: {path}")
    print(json.dumps(audit["summary"], indent=2))


if __name__ == "__main__":
    main()
