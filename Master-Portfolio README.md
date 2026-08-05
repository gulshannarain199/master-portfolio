# Master Portfolio

Welcome to my professional engineering portfolio. This repository contains practical projects, automation scripts, and technical tools developed across core technology domains, mirroring my studies in Software Development, Information Systems, and Computer & Network Technology.

---

## 📁 Project Structure

* **`01_Python_Data_Science/`**
  * Data analysis and manipulation scripts across structured modules.
* **`02_Python_Networking/`**
  * Network utilities including ping tools and connectivity checks (`ping_utility.py`).
* **`03_Network_Automation/`**
  * **`interface_parser.py`**: Parses raw network device CLI outputs into structured JSON and YAML formats.
  * **`multi_device_automation.py`**: Automates live multi-device SSH connections using Netmiko with exception handling and sandbox fallbacks.
  * **`network_health.py`**: Audits network reachability and latency with an intelligent fallback demonstration mode.
  * **`netmiko_first_script.py`**: Initial foundational script for establishing secure SSH connections to network devices using Netmiko.
  * **`dns_latency_checker.py`**: Multi-protocol tool measuring and comparing performance across traditional TCP DNS and DNS over HTTPS (DoH).

---

## 🚀 Getting Started

Clone the repository and run any of the automated scripts directly using Python 3:

```bash
git clone [https://github.com/gulshannarain199/master-portfolio.git](https://github.com/gulshannarain199/master-portfolio.git)
cd master-portfolio
python3 03_Network_Automation/network_health.py