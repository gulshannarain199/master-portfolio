
# Network Automation Portfolio

A collection of Python tools for network diagnostics and Cisco network
automation.

## Features

- DNS response checks using UDP DNS and DNS over HTTPS.
- Network reachability checks using the system ping utility.
- Cisco `show ip interface brief` output parsing.
- Multi-device SSH automation using Netmiko.
- Network diagnostic report generation in JSON, CSV and HTML.

## Requirements

Python 3.10 or later is recommended.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Generate an offline demonstration report

From this directory:

```bash
python network_diagnostic_report.py --offline
```

The offline demonstration uses the included Cisco sample output and
does not contact external hosts or network devices.

Reports are saved in the `output` directory.

## Run live network diagnostics

```bash
python network_diagnostic_report.py
```

Live mode performs DNS lookups and TCP connection checks to selected
public hosts. Results depend on the environment and network access.

## Cisco interface parser

```bash
python interface_parser.py --input raw_output.txt
```

## Network health checker

```bash
python network_health.py --count 3
```

The ping utility must be available on the operating system.

## Multi-device automation

Copy `devices.example.json` to `devices.json` and replace the example
address with an authorised device address.

Set credentials as environment variables:

```bash
export NETWORK_USERNAME="your_username"
export NETWORK_PASSWORD="your_password"
```

Then run:

```bash
python multi_device_automation.py
```

Only connect to devices you own or are authorised to administer.
Do not commit real credentials or local device configurations.

## Tests

Run:

```bash
python -m unittest discover -s tests -v
```

The tests use sample data and mocked SSH connections. They do not
require a physical Cisco device.

## Limitations

- Cisco parsing is designed around the supplied `show ip interface brief`
  output format and should be validated against other device versions.
- Live network checks depend on DNS, routing, firewall and remote-host
  availability.
- The multi-device script currently retrieves interface output; it does
  not make configuration changes to devices.
