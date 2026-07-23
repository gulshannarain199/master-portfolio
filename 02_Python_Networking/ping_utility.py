import socket

def check_port_reachability(host, port=53, timeout=3):
    print(f"Checking reachability to {host} on port {port}...")
    try:
        # Create a socket connection to test network availability
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        print(f"Success: {host} is reachable on port {port}!")
        return True
    except socket.error as e:
        print(f"Failure: Could not connect to {host}. Error: {e}")
        return False

if __name__ == "__main__":
    # Test connection to Google's public DNS IP
    check_port_reachability("8.8.8.8", 53)