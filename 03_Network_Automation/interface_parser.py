import argparse
import json
import yaml

# Set up argument parsing so users can pass a filename in the terminal
parser = argparse.ArgumentParser(description="Parse network interface outputs into JSON and YAML.")
parser.add_argument("--input", required=True, help="Path to the raw text output file")
args = parser.parse_args()

# Read the file passed via the command line
try:
    with open(args.input, "r") as f:
        raw_output = f.read()
except FileNotFoundError:
    print(f"Error: The file '{args.input}' was not found.")
    exit(1)

lines = raw_output.splitlines()
operational_interfaces = []

for line in lines:
    if not line.strip():
        continue
    
    parts = line.split()
    print(f"DEBUG: Parsed parts -> {parts}")
    
    # Check if the line has enough parts and contains 'up' for both status and protocol
    # This checks if 'up' appears in the line's later elements
    if len(parts) >= 4:
        interface_name = parts[0]
        ip_address = parts[1]
        
        # Look for 'up' in the split parts
        if "up" in parts:
            # Let's ensure it's operationally up by checking if 'up' is near the end
            if parts[-1] == "up" and parts[-2] == "up":
                interface_dict = {
                    "interface": interface_name,
                    "ip_address": ip_address,
                    "status": "up",
                    "protocol": "up"
                }
                operational_interfaces.append(interface_dict)
                print(f"Operational Interface Found: {interface_name} (IP: {ip_address})")

# Save to JSON format with explicit path
with open("03_Network_Automation/operational_interfaces.json", "w") as json_file:
    json.dump(operational_interfaces, json_file, indent=4)

# Save to YAML format with explicit path and document header
with open("03_Network_Automation/operational_interfaces.yaml", "w") as yaml_file:
    yaml_file.write("---\n")
    yaml.dump(operational_interfaces, yaml_file, sort_keys=False)

print("\nSuccessfully parsed and saved to operational_interfaces.json and operational_interfaces.yaml!")