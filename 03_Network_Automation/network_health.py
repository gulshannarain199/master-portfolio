
import subprocess
import platform
import argparse
import re
import shutil


def ping_target(host, count=1, timeout=5):
    """Perform a real ICMP ping and return its result."""

    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        command = ["ping", "-c", str(count), "-W", str(timeout), host]

    if shutil.which("ping") is None:
        return False, None, "Ping utility not found"

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 3
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            match = re.search(r"time[=<]\s*([\d.]+)\s*ms", output, re.IGNORECASE)

            latency = float(match.group(1)) if match else None

            return True, latency, "Reachable"

        return False, None, "No ping response"

    except subprocess.TimeoutExpired:
        return False, None, "Ping timed out"

    except OSError as error:
        return False, None, str(error)


def main():
    parser = argparse.ArgumentParser(
        description="Network Health and Reachability Checker"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of ping requests per target"
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    test_targets = [
        {"hostname": "Google Public DNS", "ip": "8.8.8.8"},
        {"hostname": "Cloudflare DNS", "ip": "1.1.1.1"},
        {
            "hostname": "Cisco DevNet Sandbox",
            "ip": "devnetsandboxiosxec9k.cisco.com"
        },
        {"hostname": "Documentation Test IP", "ip": "192.0.2.1"}
    ]

    print("\nNetwork Health and Reachability Audit")
    print("=" * 75)

    print(f"{'TARGET':<27} {'IP / HOST':<32} {'STATUS':<12} {'LATENCY'}")
    print("-" * 75)

    online_count = 0

    for target in test_targets:
        name = target["hostname"]
        host = target["ip"]

        is_up, latency, message = ping_target(
            host,
            count=args.count
        )

        if is_up:
            online_count += 1
            status = "ONLINE"
            latency_text = (
                f"{latency} ms" if latency is not None else "Not measured"
            )
        else:
            status = "OFFLINE"
            latency_text = message

        print(
            f"{name:<27} {host:<32} "
            f"{status:<12} {latency_text}"
        )

    print("-" * 75)
    print(f"Targets checked: {len(test_targets)}")
    print(f"Reachable: {online_count}")
    print(f"Unreachable: {len(test_targets) - online_count}")

    print("\nAudit completed. Results reflect actual ping responses.\n")


if __name__ == "__main__":
    main()
