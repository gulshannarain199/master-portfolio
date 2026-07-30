import json
from netmiko import ConnectHandler

# Load devices from the external JSON file
with open("03_Network_Automation/devices.json", "r") as file:
    devices = json.load(file)

# Loop through each device in the JSON list
for device in devices:
    print(f"\nAttempting to connect to {device['ip']}...")
    
    try:
        # Try establishing an SSH connection using Netmiko
        net_connect = ConnectHandler(**device)
        print("Connection successful!")
        
        # Run command on live device
        output = net_connect.send_command("show ip interface brief")
        print("--- Live Command Output ---")
        print(output)
        
        # Disconnect cleanly
        net_connect.disconnect()
        
    except Exception as e:
        print(f"Connection failed: {e}")
        print("[Note: Live sandbox unreachable. Displaying portfolio simulation output]")
        
        # Mock fallback data for reliable portfolio demonstration
        simulated_output = """
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet1           10.10.20.48     YES DHCP   up                    up      
GigabitEthernet2           unassigned      YES unset  administratively down down    
Loopback0                  192.168.1.1     YES manual up                    up      
"""
        print("--- Command Output ---")
        print(simulated_output)