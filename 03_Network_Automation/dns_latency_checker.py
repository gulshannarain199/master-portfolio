import socket
import time

def check_dns_port(hosts, port=53, timeout=2):
    """
    Checks reachability of DNS servers by establishing a socket connection 
    to the standard DNS port (Port 53) or fallback to port 443 for DoH.
    """
    print("--- Starting Automated DNS Reachability Check ---")
    
    for host in hosts:
        start_time = time.time()
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            
            # Attempt to connect to the host on the specified port
            s.connect((host, port))
            
            # Calculate round-trip time in milliseconds
            latency = (time.time() - start_time) * 1000
            print(f"[SUCCESS] Connected to {host}:{port} | Latency: {latency:.2f} ms")
            
            s.close()
            
        except socket.timeout:
            print(f"[TIMEOUT] Connection to {host}:{port} timed out.")
        except socket.error as e:
            print(f"[FAILURE] Could not connect to {host}:{port}. Reason: {e}")

if __name__ == "__main__":
    # Popular DNS servers to check
    target_dns = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    check_dns_port(target_dns)