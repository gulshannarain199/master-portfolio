# Windows Endpoint Diagnostics

This package is the Windows-computer diagnostic component within the Network
Automation portfolio.

## Current components

### System information
- Identifies Windows 10 and Windows 11 using the Windows build number where possible.
- Reports when the operating system cannot be confirmed as Windows 10 or 11.
- Checks availability of `ipconfig`, `ping`, `nslookup`, and `tracert`.
- Reports Python version and system architecture.

### Network configuration
- Collects network adapter names and interface indexes.
- Collects IPv4 addresses, default gateways, and DNS server addresses.
- Uses the built-in Windows PowerShell `Get-NetIPConfiguration` cmdlet.
- Normalizes single and multiple values into consistent lists.

## Safety

These components are read-only. They do not change adapter, IP, gateway, or DNS
settings. Network configuration collection does not require administrator
privileges in a normal Windows installation.

## Run a component

From the `03_Network_Automation` directory:

```powershell
python -c "from windows_diagnostics.system_info import collect_system_info, format_system_info; print(format_system_info(collect_system_info()))"
python -c "from windows_diagnostics.network_info import collect_network_info, format_network_info; print(format_network_info(collect_network_info()))"
```

## Tests

From the `03_Network_Automation` directory:

```powershell
python -m unittest discover -s tests -v
```

## Compatibility

The target is Windows 10 and Windows 11 with Python 3.10 or later. The code
uses only the Python standard library and Windows PowerShell. Compatibility
must be verified on actual Windows 10 and Windows 11 computers before being
advertised as tested.
