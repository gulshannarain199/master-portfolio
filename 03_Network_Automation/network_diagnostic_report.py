
import argparse
import csv
import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from interface_parser import parse_interfaces

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"

def dns_check(host):
    start = time.perf_counter()
    try:
        addresses = sorted({
            item[4][0] for item in socket.getaddrinfo(host, None)
        })
        return {
            "target": host,
            "status": "SUCCESS",
            "details": ", ".join(addresses),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2)
        }
    except OSError as exc:
        return {
            "target": host,
            "status": "FAILED",
            "details": str(exc),
            "latency_ms": None
        }

def tcp_check(host, port=443, timeout=3):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {
                "target": f"{host}:{port}",
                "status": "SUCCESS",
                "details": "TCP connection established",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2)
            }
    except OSError as exc:
        return {
            "target": f"{host}:{port}",
            "status": "FAILED",
            "details": str(exc),
            "latency_ms": None
        }

def build_report(offline=False):
    raw_path = BASE / "raw_output.txt"
    raw = raw_path.read_text(encoding="utf-8")
    interfaces = parse_interfaces(raw)

    if offline:
        checks = [
            {
                "target": "offline-demo.example",
                "status": "NOT_TESTED",
                "details": "Offline demonstration; no network request made",
                "latency_ms": None
            }
        ]
    else:
        checks = []
        for host in ("example.com", "google.com", "cloudflare.com"):
            checks.append(dns_check(host))
            checks.append(tcp_check(host))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_demo" if offline else "live",
        "network_checks": checks,
        "operational_interfaces": interfaces,
        "summary": {
            "checks_total": len(checks),
            "checks_successful": sum(
                item["status"] == "SUCCESS" for item in checks
            ),
            "checks_failed": sum(
                item["status"] == "FAILED" for item in checks
            ),
            "operational_interfaces": len(interfaces)
        }
    }

def write_reports(report):
    OUTPUT.mkdir(exist_ok=True)

    json_path = OUTPUT / "network_diagnostic_report.json"
    csv_path = OUTPUT / "network_diagnostic_report.csv"
    html_path = OUTPUT / "network_diagnostic_report.html"

    json_path.write_text(
        json.dumps(report, indent=4), encoding="utf-8"
    )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["target", "status", "details", "latency_ms"]
        )
        writer.writeheader()
        writer.writerows(report["network_checks"])

    rows = "".join(
        "<tr>" + "".join(
            f"<td>{str(item[key])}</td>"
            for key in ("target", "status", "details", "latency_ms")
        ) + "</tr>"
        for item in report["network_checks"]
    )

    summary = report["summary"]
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Network Diagnostic Report</title>
<style>
body {{font-family:Arial,sans-serif;margin:35px;color:#222}}
table {{border-collapse:collapse;width:100%}}
th,td {{border:1px solid #ccc;padding:9px;text-align:left}}
th {{background:#eee}}
</style>
</head>
<body>
<h1>Network Diagnostic Report</h1>
<p>Generated: {report["generated_at"]}</p>
<p>Mode: {report["mode"]}</p>
<h2>Summary</h2>
<ul>
<li>Checks: {summary["checks_total"]}</li>
<li>Successful: {summary["checks_successful"]}</li>
<li>Failed: {summary["checks_failed"]}</li>
<li>Operational interfaces: {summary["operational_interfaces"]}</li>
</ul>
<h2>Network checks</h2>
<table>
<tr><th>Target</th><th>Status</th><th>Details</th><th>Latency ms</th></tr>
{rows}
</table>
<h2>Operational interfaces</h2>
<ul>
{''.join(f"<li>{i['interface']} — {i['ip_address']}</li>" for i in report["operational_interfaces"])}
</ul>
</body></html>"""

    html_path.write_text(html, encoding="utf-8")
    return json_path, csv_path, html_path

def main():
    parser = argparse.ArgumentParser(
        description="Generate a network diagnostic report."
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="Generate a demonstration report without network requests."
    )
    args = parser.parse_args()

    report = build_report(offline=args.offline)
    paths = write_reports(report)

    print("Network diagnostic report generated.")
    print("Mode:", report["mode"])
    print("Summary:", json.dumps(report["summary"]))
    for path in paths:
        print("Report:", path)

if __name__ == "__main__":
    main()
