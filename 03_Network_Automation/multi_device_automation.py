
import json
import os
from pathlib import Path
from netmiko import ConnectHandler


# Resolve devices.json relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
DEVICES_FILE = SCRIPT_DIR / "devices.json"


def load_devices():
    """Load network devices from the JSON configuration file."""

    if not DEVICES_FILE.exists():
        raise FileNotFoundError(
            f"Device configuration not found: {DEVICES_FILE}"
        )

    with DEVICES_FILE.open("r", encoding="utf-8") as file:
        devices = json.load(file)

    if not isinstance(devices, list):
        raise ValueError("devices.json must contain a JSON list.")

    return devices


def connect_to_device(device):
    """Connect to a network device and retrieve interface information."""

    device_name = device.get("host") or device.get("ip", "Unknown device")

    connection = None

    try:
        # Read credentials from environment variables
        username = os.getenv("NETWORK_USERNAME")
        password = os.getenv("NETWORK_PASSWORD")

        if not username or not password:
            raise ValueError(
                "Set NETWORK_USERNAME and NETWORK_PASSWORD "
                "environment variables before connecting."
            )

        # Prepare Netmiko connection settings
        connection_settings = device.copy()

        connection_settings.pop("password", None)
        connection_settings["username"] = username
        connection_settings["password"] = password

        # Support either host or ip in devices.json
        if "host" not in connection_settings:
            connection_settings["host"] = connection_settings.pop("ip", None)

        if not connection_settings.get("host"):
            raise ValueError("Device configuration is missing its host or IP.")

        if not connection_settings.get("device_type"):
            raise ValueError("Device configuration is missing device_type.")

        connection_settings.update({
            "conn_timeout": 10,
            "auth_timeout": 10,
            "banner_timeout": 10
        })

        print(f"\nConnecting to {device_name}...")

        connection = ConnectHandler(**connection_settings)

        print("SSH connection successful.")

        output = connection.send_command(
            "show ip interface brief",
            read_timeout=30
        )

        print("\n--- Actual Device Command Output ---")
        print(output)

        print("\nDevice check completed.")

    except Exception as error:
        print(f"\nConnection or command failed for {device_name}.")
        print(f"Error: {type(error).__name__}: {error}")
        print("No simulated device output will be displayed.")

    finally:
        if connection is not None:
            try:
                connection.disconnect()
                print(f"Disconnected from {device_name}.")
            except Exception as error:
                print(f"Warning: Disconnect failed: {error}")


def main():
    try:
        devices = load_devices()

        if not devices:
            print("No devices found in devices.json.")
            return

        print(f"Loaded {len(devices)} device(s).")

        for device in devices:
            if not isinstance(device, dict):
                print("Skipping invalid device entry.")
                continue

            connect_to_device(device)

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}")


if __name__ == "__main__":
    main()
