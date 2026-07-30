from netmiko import ConnectHandler

# Define your device dictionary using key-value pairs
cisco_device = {
    "device_type": "cisco_ios",
    "ip": "sandbox-iosxe-recomm-1.cisco.com",
    "username": "developer",
    "password": "C1sco12345",   # Note the capital 'C' and number '1'
    "port": 22,
}

try:
    print(f"Connecting to {cisco_device['ip']}...")
    
    # Establish the connection
    net_connect = ConnectHandler(**cisco_device)
    
    # Run a command
    output = net_connect.send_command("show ip interface brief")
    print("\n--- Command Output ---")
    print(output)
    
    # Disconnect cleanly
    net_connect.disconnect()

except Exception as e:
    print(f"Connection failed: {e}")