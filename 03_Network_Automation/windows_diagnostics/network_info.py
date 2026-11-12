"""Collect Windows network adapter configuration using PowerShell.

The collector is read-only. It does not change adapter, IP, gateway, or DNS
configuration.
"""

import json
import platform
import subprocess


POWERSHELL_COMMAND = r"""
Get-NetIPConfiguration | ForEach-Object {
    [pscustomobject]@{
        InterfaceAlias = $_.InterfaceAlias
        InterfaceIndex = $_.InterfaceIndex
        IPv4Address = @($_.IPv4Address | ForEach-Object { $_.IPAddress })
        DefaultGateway = @($_.IPv4DefaultGateway | ForEach-Object { $_.NextHop })
        DNSServers = @($_.DNSServer.ServerAddresses)
    }
} | ConvertTo-Json -Depth 4 -Compress
"""


def _as_list(value):
    """Normalize PowerShell JSON values that may be null, scalar, or arrays."""
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item not in (None, "")]
    return [value] if value != "" else []


def parse_network_configuration(output):
    """Parse Get-NetIPConfiguration JSON into a consistent list of adapters."""
    if not output or not output.strip():
        return []

    decoded = json.loads(output)
    records = decoded if isinstance(decoded, list) else [decoded]
    adapters = []

    for record in records:
        if not isinstance(record, dict):
            continue

        adapters.append({
            "interface_alias": record.get("InterfaceAlias"),
            "interface_index": record.get("InterfaceIndex"),
            "ipv4_addresses": _as_list(record.get("IPv4Address")),
            "default_gateways": _as_list(record.get("DefaultGateway")),
            "dns_servers": _as_list(record.get("DNSServers")),
        })

    return adapters


def collect_network_info(timeout=20):
    """Collect network configuration on Windows, returning errors as data."""
    if platform.system().lower() != "windows":
        return {
            "status": "UNSUPPORTED",
            "adapters": [],
            "error": "Network configuration collection currently supports Windows 10 and 11.",
        }

    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                POWERSHELL_COMMAND,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "PowerShell command failed").strip()
            return {"status": "FAILED", "adapters": [], "error": detail}

        adapters = parse_network_configuration(completed.stdout)
        return {
            "status": "SUCCESS",
            "adapters": adapters,
            "error": None if adapters else "No IP configurations were returned.",
        }

    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {
            "status": "FAILED",
            "adapters": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def format_network_info(result):
    """Format adapter configuration for a readable diagnostic report."""
    lines = ["NETWORK CONFIGURATION", "=====================",
             f"Collection status: {result['status']}"]

    for number, adapter in enumerate(result["adapters"], start=1):
        lines.extend([
            "",
            f"Adapter {number}: {adapter['interface_alias'] or 'Unknown'}",
            f"Interface index: {adapter['interface_index'] or 'Unknown'}",
            "IPv4 address(es): " + (", ".join(map(str, adapter["ipv4_addresses"])) or "None"),
            "Default gateway(s): " + (", ".join(map(str, adapter["default_gateways"])) or "None"),
            "DNS server(s): " + (", ".join(map(str, adapter["dns_servers"])) or "None"),
        ])

    if result.get("error"):
        lines.extend(["", f"Note: {result['error']}"])

    return "\n".join(lines)
