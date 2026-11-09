
import argparse
import json
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed.")
    print("Install it using: python -m pip install PyYAML")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_interfaces(raw_output):
    """Parse Cisco show ip interface brief output."""

    operational_interfaces = []

    for line in raw_output.splitlines():
        parts = line.split()

        if len(parts) < 6:
            continue

        # Skip table headings and separator lines
        if parts[0].lower() == "interface":
            continue

        if set(line.strip()) <= {"-", "="}:
            continue

        interface_name = parts[0]
        ip_address = parts[1]
        protocol = parts[-1]

        # Handle multi-word interface status
        if len(parts) >= 7 and parts[-3:-1] == [
            "administratively", "down"
        ]:
            status = "administratively down"
        else:
            status = parts[-2]

        # Keep only interfaces that are operationally up
        if status.lower() == "up" and protocol.lower() == "up":
            operational_interfaces.append({
                "interface": interface_name,
                "ip_address": ip_address,
                "status": status,
                "protocol": protocol
            })

    return operational_interfaces


def main():
    parser = argparse.ArgumentParser(
        description="Parse Cisco interface output into JSON and YAML."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the raw Cisco interface output file"
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser()

    if not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")

    try:
        raw_output = input_path.read_text(encoding="utf-8")

        interfaces = parse_interfaces(raw_output)

        json_path = SCRIPT_DIR / "operational_interfaces.json"
        yaml_path = SCRIPT_DIR / "operational_interfaces.yaml"

        json_path.write_text(
            json.dumps(interfaces, indent=4),
            encoding="utf-8"
        )

        yaml_path.write_text(
            yaml.safe_dump(
                interfaces,
                sort_keys=False,
                allow_unicode=True
            ),
            encoding="utf-8"
        )

        print("\nInterface parsing completed.")
        print(f"Operational interfaces found: {len(interfaces)}")
        print(f"JSON report: {json_path}")
        print(f"YAML report: {yaml_path}")

    except (OSError, UnicodeError) as error:
        print(f"File processing error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
