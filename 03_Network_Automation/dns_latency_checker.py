import socket
import time
import urllib.request
import json

def check_tcp_dns(hosts, port=53, timeout=2):
    print("\n--- 1. Testing Traditional TCP DNS (Port 53) ---")
    for host in hosts:
        start_time = time.time()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            latency = (time.time() - start_time) * 1000
            print(f"[SUCCESS] Connected to {host}:{port} | Latency: {latency:.2f} ms")
            s.close()
        except socket.timeout:
            print(f"[TIMEOUT] Connection to {host}:{port} timed out.")
        except socket.error as e:
            print(f"[FAILURE] Could not connect to {host}:{port}. Reason: {e}")

def check_doh():
    print("\n--- 2. Testing DNS over HTTPS - DoH (Port 443) ---")
    doh_providers = {
        "Cloudflare": "https://cloudflare-dns.com/dns-query?name=example.com&type=A",
        "Google": "https://dns.google/resolve?name=example.com&type=A"
    }
    
    headers = {
        "Accept": "application/dns-json"
    }
    
    for provider, url in doh_providers.items():
        start_time = time.time()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                latency = (time.time() - start_time) * 1000
                if response.getcode() == 200:
                    print(f"[SUCCESS] {provider} DoH Responded | Latency: {latency:.2f} ms")
                else:
                    print(f"[WARNING] {provider} returned status code {response.getcode()}")
        except urllib.error.URLError as e:
            print(f"[FAILURE] Could not reach {provider} DoH. Reason: {e.reason}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred with {provider}: {e}")

if __name__ == "__main__":
    target_dns = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    
    print("=== Starting Network Automation: DNS & DoH Health Audit ===")
    check_tcp_dns(target_dns)
    check_doh()
    print("\n=== Audit Complete ===")