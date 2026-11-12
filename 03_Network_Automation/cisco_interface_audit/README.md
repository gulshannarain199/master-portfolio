# Cisco Interface Audit

A remote-deliverable Python utility for analysing client-supplied Cisco IOS `show ip interface brief` text captures.

## Why this is useful

A client runs the read-only show command on their own authorised device, saves the output to a text file, and securely shares that file. The freelancer can analyse the evidence without visiting the site or receiving device credentials.

## Features

- Parses operational, down, and administratively down interface states.
- Preserves source line numbers for traceability.
- Counts interface states and provides cautious next-step recommendations.
- Generates JSON, CSV, and HTML reports.
- Escapes untrusted text in the HTML report.
- Uses only the Python standard library.

## Run

From the `03_Network_Automation` directory:

```bash
python -m cisco_interface_audit.analyzer --input cisco_interface_audit/sample_show_ip_interface_brief.txt
```

Reports are written to `interface_audit_output/`. Use `--output-dir` to choose another directory.

## Tests

From the `03_Network_Automation` directory:

```bash
python -m unittest tests.test_cisco_interface_audit -v
```

## Client workflow

1. Confirm the device model, software version, and exact issue.
2. Ask for the appropriate read-only command output. Remind the client to remove passwords, keys, usernames, public IPs, serial numbers, and other sensitive details when they are not needed.
3. Receive the file using the freelance platform's approved file-sharing method.
4. Run the analyzer and review findings in context.
5. Deliver evidence, limitations, and recommended next checks.

## Limitations

This first version supports the standard Cisco IOS `show ip interface brief` table. It does not connect to or modify devices, prove root cause, or cover every Cisco platform/output variation. A down interface may be intentionally unused. Recommendations must be confirmed against the client's topology and requirements before any change is made.
