from netmiko import ConnectHandler

# Define your device dictionary using key-value pairs
cisco_device = {
    "device_type": "cisco_ios",
    "ip": "devnetsandboxiosxec9k.cisco.com",
    "username": "developer",
    "password": "C1sco12345!",
    "port": 22,
}

try:
    print(f"Connecting to {cisco_device['ip']}...")
    
    # Establish the connection
    net_connect = ConnectHandler(**cisco_device)
    
    # Run a command
    output = net_connect.send_command("show ip interface brief")
    print("\n--- Live Command Output ---")
    print(output)
    
    # Disconnect cleanly
    net_connect.disconnect()

except Exception as e:
    print(f"\n[Note: Live sandbox unreachable. Displaying portfolio simulation output]")
    simulated_output = """
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet1           10.10.20.48     YES DHCP   up                    up      
GigabitEthernet2           unassigned      YES unset  administratively down down    
Loopback0                  192.168.1.1     YES manual up                    up      
    """
    print("\n--- Command Output ---")
    print(simulated_output)