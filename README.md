### Phase 1: Interface Parser (`interface_parser.py`)
* **Purpose:** Parses raw CLI output into structured data.
* **Usage:** `python3 03_Network_Automation/interface_parser.py --input 03_Network_Automation/raw_output.txt`

### Phase 2: Multi-Device SSH Manager (`multi_device_automation.py`)
* **Purpose:** Automates live SSH connections.
* **Usage:** `python3 03_Network_Automation/multi_device_automation.py`

### Phase 3: Network Health (`network_health.py`)
* **Purpose:** Audits network reachability.
* **Usage:** `python3 03_Network_Automation/network_health.py`

## Additional Scripts & Utilities
* **Netmiko First Connection (`netmiko_first_script.py`):** Initial foundational script for establishing secure SSH connections to Cisco devices via Netmiko.
  * *Usage:* `python3 03_Network_Automation/netmiko_first_script.py`
* **DNS Latency Checker (`dns_latency_checker.py`):** Multi-protocol utility measuring performance across traditional TCP DNS (Port 53) and DNS over HTTPS (DoH - Port 443).
  * *Usage:* `python3 03_Network_Automation/dns_latency_checker.py`
