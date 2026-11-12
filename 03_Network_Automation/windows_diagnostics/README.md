# Windows Endpoint Diagnostics

This package is the first Windows-computer diagnostic component within the
Network Automation portfolio.

## Current component

- Identifies Windows 10 and Windows 11 using the Windows build number where possible.
- Reports when the operating system cannot be confirmed as Windows 10 or 11.
- Checks whether `ipconfig`, `ping`, `nslookup`, and `tracert` are available.
- Reports Python version and system architecture.

## Safety

This component is read-only. It does not change network settings and does not
send network probes.

## Run

From the `03_Network_Automation` directory:

```powershell
python -c "from windows_diagnostics.system_info import collect_system_info, format_system_info; print(format_system_info(collect_system_info()))"
```

## Tests

From the `03_Network_Automation` directory:

```powershell
python -m unittest discover -s tests -v
```

## Compatibility

The target is Windows 10 and Windows 11 with Python 3.10 or later. The code
uses only the Python standard library. Compatibility must be verified on
actual Windows 10 and Windows 11 computers before being advertised as tested.
