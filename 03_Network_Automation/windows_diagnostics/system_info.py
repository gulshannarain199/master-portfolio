"""Collect basic Windows system details and check diagnostic command availability.

This module is read-only. It does not change network settings or execute
network diagnostic commands.
"""

import platform
import re
import shutil


REQUIRED_COMMANDS = ("ipconfig", "ping", "nslookup", "tracert")


def _windows_build(version_string):
    """Extract the Windows build number from a version string when available."""
    matches = re.findall(r"\d+", version_string or "")
    return int(matches[-1]) if matches else None


def identify_windows(system=None, release=None, version=None):
    """Identify Windows 10/11 using the build number where possible."""
    system = system if system is not None else platform.system()
    release = release if release is not None else platform.release()
    version = version if version is not None else platform.version()

    if system.lower() != "windows":
        return {
            "name": system,
            "supported": False,
            "reason": "This first release targets Windows 10 and Windows 11.",
        }

    build = _windows_build(version)

    # Windows 11 starts at build 22000. Windows 10 builds start at 10240.
    if build is not None and build >= 22000:
        name = "Windows 11"
    elif build is not None and 10240 <= build < 22000:
        name = "Windows 10"
    elif release in ("10", "11"):
        # Do not guess Windows 10 vs 11 when the build number is unavailable.
        name = f"Windows release {release} (build not identified)"
    else:
        name = f"Windows {release}"

    supported = name in ("Windows 10", "Windows 11")
    return {
        "name": name,
        "supported": supported,
        "build": build,
        "reason": None if supported else "Windows version could not be confirmed as Windows 10 or 11.",
    }


def collect_system_info():
    """Return system details and availability of common network commands."""
    system = platform.system()
    release = platform.release()
    version = platform.version()
    os_info = identify_windows(system=system, release=release, version=version)

    commands = {
        command: shutil.which(command) is not None
        for command in REQUIRED_COMMANDS
    }

    return {
        "operating_system": system,
        "windows": os_info,
        "windows_release": release,
        "windows_version": version,
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "commands": commands,
    }


def format_system_info(info):
    """Format collected information as a readable text report."""
    windows = info["windows"]
    lines = [
        "SYSTEM INFORMATION",
        "==================",
        f"Operating system: {info['operating_system']}",
        f"Detected version: {windows['name']}",
        f"Supported by this release: {'Yes' if windows['supported'] else 'No'}",
        f"Windows version/build: {info['windows_version']}",
        f"Architecture: {info['architecture']}",
        f"Python version: {info['python_version']}",
        "",
        "NETWORK COMMAND AVAILABILITY",
        "============================",
    ]

    for command, available in info["commands"].items():
        lines.append(f"{command}: {'Available' if available else 'Not found'}")

    if windows["reason"]:
        lines.extend(["", f"Note: {windows['reason']}"])

    missing = [name for name, available in info["commands"].items() if not available]
    if missing:
        lines.extend(["", "Missing commands: " + ", ".join(missing)])

    return "\n".join(lines)
